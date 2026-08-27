"use client";
import Link from "next/link";
import {useSearchParams} from "next/navigation";
import {Suspense} from "react";

function CompleteContent(){
  const query=useSearchParams();
  const onsite=query.get("method")==="ONSITE";
  return <main className="grid min-h-screen place-items-center bg-mist p-5"><section className="card max-w-lg p-8 text-center"><div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-amber-50 text-3xl text-amber-600">✓</div><h1 className="mt-5 text-2xl font-bold">신청이 접수되었습니다</h1><p className="mt-3 leading-6 text-slate-500">현재 상태는 <b className="text-amber-700">결제대기</b>입니다.<br/>관리자가 납부를 확인하면 Zoom 참가 링크를 이메일로 보내드립니다.</p>{onsite?<div className="mt-6 rounded-xl bg-mist p-5 text-left text-sm"><b>현장결제 안내</b><p className="mt-2 text-slate-600">교육 당일 접수처에서 신청자 성함을 알려주시고 교육비를 납부해 주세요.</p></div>:<div className="mt-6 rounded-xl bg-mist p-5 text-left text-sm"><b>입금 계좌</b><dl className="mt-3 grid grid-cols-[90px_1fr] gap-2"><dt className="text-slate-500">은행</dt><dd>{query.get("bank")||"신한은행"}</dd><dt className="text-slate-500">계좌번호</dt><dd className="font-bold">{query.get("account")||"110-000-000000"}</dd><dt className="text-slate-500">예금주</dt><dd>{query.get("holder")||"에듀페이링크"}</dd><dt className="text-slate-500">입금자명</dt><dd>신청자 이름과 동일하게</dd></dl></div>}<div className="mt-5 rounded-xl border border-blue-100 bg-blue-50 p-4 text-left text-xs leading-5 text-blue-800">입금 후 반영까지 시간이 걸릴 수 있습니다. 입금자명이 다른 경우 운영 담당자에게 알려주세요.</div><Link href="/" className="btn btn-primary mt-6 w-full">확인</Link></section></main>
}

export default function Complete(){return <Suspense fallback={<main className="grid min-h-screen place-items-center bg-mist">신청 내용을 확인하는 중...</main>}><CompleteContent/></Suspense>}
