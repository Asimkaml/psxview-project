import { useCallback, useEffect, useState } from 'react';
import { dashboardRepository } from '../data/repository';
import type { DashboardSummary } from '../types/dashboard';

export function useDashboard(){ const [data,setData]=useState<DashboardSummary|null>(null); const [error,setError]=useState(''); const [attempt,setAttempt]=useState(0); const retry=useCallback(()=>setAttempt(v=>v+1),[]); useEffect(()=>{ const controller=new AbortController(); setError(''); dashboardRepository.getSummary(controller.signal).then(setData).catch(e=>{if(e.name!=='AbortError')setError(e instanceof Error?e.message:'Unable to load dashboard');}); return()=>controller.abort(); },[attempt]); return {data,error,loading:!data&&!error,retry}; }
