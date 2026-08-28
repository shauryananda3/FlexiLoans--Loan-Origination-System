from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
import sqlite3, json, uuid

BASE = Path(__file__).resolve().parent
DB = BASE / 'los.db'

app = FastAPI(title='FlexiLoans LOS', version='1.0.0', description='Educational Technical BA portfolio prototype')
app.mount('/static', StaticFiles(directory=BASE / 'static'), name='static')

STAGES = ['SUBMITTED','KYC_VERIFIED','CREDIT_COMPLETED','APPROVED','DOCUMENTS_COMPLETED','MANDATE_COMPLETED','READY_FOR_DISBURSEMENT','DISBURSED']

class ApplicationIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    pan: str = Field(min_length=10, max_length=10)
    employment_type: str
    income: float = Field(gt=0)
    requested_amount: float = Field(gt=0, le=500000)
    tenure_months: int = Field(gt=0, le=60)

class FailureIn(BaseModel):
    integration: str
    application_id: int


def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS applications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      application_no TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      pan TEXT NOT NULL,
      employment_type TEXT NOT NULL,
      income REAL NOT NULL,
      requested_amount REAL NOT NULL,
      tenure_months INTEGER NOT NULL,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      cibil_score INTEGER,
      kyc_status TEXT,
      fraud_status TEXT,
      decision_reason TEXT,
      disbursement_ref TEXT
    );
    CREATE TABLE IF NOT EXISTS integration_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      application_id INTEGER NOT NULL,
      integration TEXT NOT NULL,
      status TEXT NOT NULL,
      response TEXT,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS audit_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      application_id INTEGER NOT NULL,
      event_type TEXT NOT NULL,
      old_status TEXT,
      new_status TEXT,
      actor TEXT NOT NULL,
      details TEXT,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS documents (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      application_id INTEGER NOT NULL,
      document_type TEXT NOT NULL,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    ''')
    c.commit(); c.close()

init_db()

def now(): return datetime.now(timezone.utc).isoformat()

def audit(c, app_id, event_type, old, new, details='', actor='SYSTEM'):
    c.execute('INSERT INTO audit_events(application_id,event_type,old_status,new_status,actor,details,created_at) VALUES(?,?,?,?,?,?,?)',
              (app_id,event_type,old,new,actor,details,now()))

def get_app(c, app_id):
    row=c.execute('SELECT * FROM applications WHERE id=?',(app_id,)).fetchone()
    if not row: raise HTTPException(404,'Application not found')
    return row

def rowdict(r): return dict(r) if r else None

@app.get('/')
def home(): return FileResponse(BASE/'static'/'index.html')

@app.get('/api/health')
def health(): return {'status':'UP','service':'flexiloans-los','time':now()}

@app.post('/api/applications')
def create_application(x: ApplicationIn):
    c=db(); ts=now(); no='FL-'+uuid.uuid4().hex[:8].upper()
    cur=c.execute('''INSERT INTO applications(application_no,name,pan,employment_type,income,requested_amount,tenure_months,status,created_at,updated_at)
                     VALUES(?,?,?,?,?,?,?,?,?,?)''',(no,x.name,x.pan.upper(),x.employment_type,x.income,x.requested_amount,x.tenure_months,'SUBMITTED',ts,ts))
    app_id=cur.lastrowid; audit(c,app_id,'APPLICATION_CREATED',None,'SUBMITTED','Customer application created','CUSTOMER'); c.commit();
    return rowdict(get_app(c,app_id))

@app.get('/api/applications')
def applications():
    c=db(); return [rowdict(r) for r in c.execute('SELECT * FROM applications ORDER BY id DESC').fetchall()]

@app.get('/api/applications/{app_id}')
def application(app_id:int):
    c=db(); return rowdict(get_app(c,app_id))

@app.get('/api/applications/{app_id}/audit')
def audit_trail(app_id:int):
    c=db(); get_app(c,app_id)
    return [rowdict(r) for r in c.execute('SELECT * FROM audit_events WHERE application_id=? ORDER BY id',(app_id,)).fetchall()]

@app.get('/api/applications/{app_id}/integrations')
def integration_events(app_id:int):
    c=db(); get_app(c,app_id)
    return [rowdict(r) for r in c.execute('SELECT * FROM integration_events WHERE application_id=? ORDER BY id',(app_id,)).fetchall()]

def integration(c, app_id, name, status, response):
    c.execute('INSERT INTO integration_events(application_id,integration,status,response,created_at) VALUES(?,?,?,?,?)',
              (app_id,name,status,json.dumps(response),now()))

@app.post('/api/applications/{app_id}/kyc')
def kyc(app_id:int):
    c=db(); r=get_app(c,app_id); old=r['status']
    if old not in ['SUBMITTED']: raise HTTPException(409,f'KYC not allowed from {old}')
    result={'pan_verified':True,'address_verified':True,'provider':'MOCK_CKYC'}
    integration(c,app_id,'KYC','SUCCESS',result)
    c.execute("UPDATE applications SET kyc_status='VERIFIED',status='KYC_VERIFIED',updated_at=? WHERE id=?",(now(),app_id))
    audit(c,app_id,'KYC_COMPLETED',old,'KYC_VERIFIED','Mock KYC verification passed')
    c.commit(); return rowdict(get_app(c,app_id))

@app.post('/api/applications/{app_id}/credit')
def credit(app_id:int):
    c=db(); r=get_app(c,app_id); old=r['status']
    if old!='KYC_VERIFIED': raise HTTPException(409,f'Credit not allowed from {old}')
    score=760 if r['income']>=25000 else 690
    result={'bureau':'MOCK_CIBIL','credit_score':score,'bureau_status':'SUCCESS'}
    integration(c,app_id,'CIBIL','SUCCESS',result)
    c.execute("UPDATE applications SET cibil_score=?,status='CREDIT_COMPLETED',updated_at=? WHERE id=?",(score,now(),app_id))
    audit(c,app_id,'CREDIT_COMPLETED',old,'CREDIT_COMPLETED',f'Mock CIBIL score={score}')
    c.commit(); return rowdict(get_app(c,app_id))

@app.post('/api/applications/{app_id}/decision')
def decision(app_id:int):
    c=db(); r=get_app(c,app_id); old=r['status']
    if old!='CREDIT_COMPLETED': raise HTTPException(409,f'Decision not allowed from {old}')
    approved=(r['cibil_score'] or 0)>=750 and r['requested_amount']<=500000
    fraud={'status':'CLEAR','provider':'MOCK_FRAUD'}; integration(c,app_id,'FRAUD_PEP','SUCCESS',fraud)
    if approved:
        new='APPROVED'; reason='Illustrative BRE: credit score >= 750 and amount within product limit.'
    else:
        new='REJECTED'; reason='Illustrative BRE rule not satisfied.'
    c.execute('UPDATE applications SET fraud_status=?,status=?,decision_reason=?,updated_at=? WHERE id=?',('CLEAR',new,reason,now(),app_id))
    audit(c,app_id,'BRE_DECISION',old,new,reason,'DECISION_ENGINE'); c.commit()
    return rowdict(get_app(c,app_id))

@app.post('/api/applications/{app_id}/documents')
def documents(app_id:int):
    c=db(); r=get_app(c,app_id)
    if r['status']!='APPROVED': raise HTTPException(409,'Documents require APPROVED status')
    old=r['status']
    for typ in ['SANCTION_LETTER','LOAN_AGREEMENT','REPAYMENT_SCHEDULE']:
        c.execute('INSERT INTO documents(application_id,document_type,status,created_at) VALUES(?,?,?,?)',(app_id,typ,'GENERATED',now()))
    c.execute("UPDATE applications SET status='DOCUMENTS_COMPLETED',updated_at=? WHERE id=?",(now(),app_id))
    audit(c,app_id,'DOCUMENTS_GENERATED',old,'DOCUMENTS_COMPLETED','Three mock loan documents generated')
    c.commit(); return {'status':'DOCUMENTS_COMPLETED','documents':[dict(x) for x in c.execute('SELECT * FROM documents WHERE application_id=?',(app_id,)).fetchall()]}

@app.post('/api/applications/{app_id}/mandate')
def mandate(app_id:int):
    c=db(); r=get_app(c,app_id)
    if r['status']!='DOCUMENTS_COMPLETED': raise HTTPException(409,'Mandate requires documents completed')
    old=r['status']; integration(c,app_id,'E_MANDATE','SUCCESS',{'mandate_status':'ACTIVE','provider':'MOCK_MANDATE'})
    c.execute("UPDATE applications SET status='MANDATE_COMPLETED',updated_at=? WHERE id=?",(now(),app_id))
    audit(c,app_id,'MANDATE_COMPLETED',old,'MANDATE_COMPLETED','Mock e-mandate registered')
    c.commit(); return rowdict(get_app(c,app_id))

@app.post('/api/applications/{app_id}/esign')
def esign(app_id:int):
    c=db(); r=get_app(c,app_id)
    if r['status']!='DOCUMENTS_COMPLETED': raise HTTPException(409,'E-sign requires documents completed')
    integration(c,app_id,'E_SIGN','SUCCESS',{'signature_status':'SIGNED','provider':'MOCK_ESIGN'})
    audit(c,app_id,'E_SIGN_COMPLETED',r['status'],r['status'],'Mock e-sign completed')
    c.commit(); return {'status':'SIGNED'}

@app.post('/api/applications/{app_id}/disburse')
def disburse(app_id:int):
    c=db(); r=get_app(c,app_id)
    if r['status']!='MANDATE_COMPLETED': raise HTTPException(409,'Disbursement requires mandate completed')
    old=r['status']; ref='DISB-'+uuid.uuid4().hex[:10].upper()
    integration(c,app_id,'DISBURSEMENT','SUCCESS',{'reference':ref,'amount':r['requested_amount']})
    c.execute("UPDATE applications SET status='DISBURSED',disbursement_ref=?,updated_at=? WHERE id=?",(ref,now(),app_id))
    audit(c,app_id,'DISBURSEMENT_COMPLETED',old,'DISBURSED',f'Disbursement reference={ref}','DISBURSEMENT_SERVICE')
    c.commit(); return rowdict(get_app(c,app_id))

@app.post('/api/simulate-failure')
def simulate_failure(x: FailureIn):
    c=db(); r=get_app(c,x.application_id)
    integration(c,x.application_id,x.integration,'FAILED',{'error':'TIMEOUT','retryable':True})
    audit(c,x.application_id,'INTEGRATION_FAILURE',r['status'],r['status'],f'{x.integration} timeout; application state preserved')
    c.commit(); return {'application_id':x.application_id,'integration':x.integration,'status':'FAILED','recommended_action':'retry_or_reprocess'}

@app.get('/api/applications/{app_id}/documents')
def docs(app_id:int):
    c=db(); get_app(c,app_id); return [rowdict(r) for r in c.execute('SELECT * FROM documents WHERE application_id=?',(app_id,)).fetchall()]
