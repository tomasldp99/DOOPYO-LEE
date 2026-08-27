"use client";

import {FormEvent,useState} from "react";
import {CheckCircleIcon,KeyIcon,ShieldCheckIcon} from "@heroicons/react/24/outline";
import AdminShell from "@/components/AdminShell";
import {api} from "@/lib/api";

export default function Settings(){
  const [error,setError]=useState("");
  const [success,setSuccess]=useState("");
  const [saving,setSaving]=useState(false);

  async function submit(e:FormEvent<HTMLFormElement>){
    e.preventDefault(); setError(""); setSuccess("");
    const form=e.currentTarget; const data=new FormData(form);
    const current_password=String(data.get("current_password")||"");
    const new_password=String(data.get("new_password")||"");
    const confirm_password=String(data.get("confirm_password")||"");
    if(new_password!==confirm_password){setError("새 비밀번호가 서로 일치하지 않습니다.");return}
    setSaving(true);
    try{
      const result=await api<{access_token:string}>("/auth/change-password",{method:"POST",body:JSON.stringify({current_password,new_password})});
      localStorage.setItem("edupay_token",result.access_token); form.reset();
      setSuccess("비밀번호가 변경되었습니다. 다른 기기의 기존 로그인은 모두 해제되었습니다.");
    }catch(x){setError(x instanceof Error?x.message:"비밀번호를 변경하지 못했습니다")}
    finally{setSaving(false)}
  }

  return <AdminShell title="설정"><div className="mx-auto max-w-3xl">
    <div className="mb-6"><h2 className="text-2xl font-bold">관리자 계정</h2><p className="mt-1 text-sm text-slate-500">관리자 로그인 비밀번호와 계정 보안을 관리하세요.</p></div>
    <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
      <form onSubmit={submit} className="card p-6 md:p-7">
        <div className="mb-6 flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-50 text-brand"><KeyIcon className="h-6 w-6"/></span><div><h3 className="font-bold">비밀번호 변경</h3><p className="text-sm text-slate-500">안전한 새 비밀번호를 입력해 주세요.</p></div></div>
        <div className="space-y-5">
          <label><span className="label">현재 비밀번호</span><input className="field" name="current_password" type="password" autoComplete="current-password" minLength={8} maxLength={128} required/></label>
          <label><span className="label">새 비밀번호</span><input className="field" name="new_password" type="password" autoComplete="new-password" minLength={8} maxLength={128} required/><span className="mt-2 block text-xs text-slate-400">8자 이상으로 설정해 주세요.</span></label>
          <label><span className="label">새 비밀번호 확인</span><input className="field" name="confirm_password" type="password" autoComplete="new-password" minLength={8} maxLength={128} required/></label>
        </div>
        {error&&<p role="alert" className="mt-5 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
        {success&&<p role="status" className="mt-5 flex items-start gap-2 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700"><CheckCircleIcon className="mt-0.5 h-5 w-5 shrink-0"/>{success}</p>}
        <div className="mt-6 flex justify-end"><button className="btn btn-primary min-w-36 disabled:cursor-not-allowed disabled:opacity-60" disabled={saving}>{saving?"변경 중…":"비밀번호 변경"}</button></div>
      </form>
      <aside className="card h-fit p-6"><ShieldCheckIcon className="mb-4 h-8 w-8 text-brand"/><h3 className="font-bold">계정 보안 안내</h3><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-500"><li>• 다른 서비스와 다른 비밀번호를 사용하세요.</li><li>• 변경 즉시 이전 로그인 정보는 무효화됩니다.</li><li>• 비밀번호를 타인과 공유하지 마세요.</li></ul></aside>
    </div>
  </div></AdminShell>
}