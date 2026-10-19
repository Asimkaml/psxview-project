import type { DashboardRepository, DashboardSummary, DataState } from '../types/dashboard';
import { dashboardFixture } from './fixtures';

class FixtureRepository implements DashboardRepository { async getSummary(signal?:AbortSignal){ await new Promise(r=>setTimeout(r,450)); if(signal?.aborted) throw new DOMException('Aborted','AbortError'); return dashboardFixture; } }
class ApiRepository implements DashboardRepository { constructor(private base:string){} async getSummary(signal?:AbortSignal):Promise<DashboardSummary>{ const response=await fetch(`${this.base}/api/dashboard`,{signal}); if(!response.ok) throw new Error(`Dashboard request failed (${response.status})`); return response.json() as Promise<DashboardSummary>; } }
const base=(import.meta.env.VITE_API_BASE_URL as string|undefined)?.replace(/\/$/,'');
export const dashboardRepository:DashboardRepository=base?new ApiRepository(base):new FixtureRepository();
export const dataState:DataState=base?{mode:'api',label:'Backend connected'}:{mode:'fixture',label:'Prototype data'};
