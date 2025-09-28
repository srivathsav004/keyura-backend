from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from database import supabase

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


class CreateContractRequest(BaseModel):
    userid: int
    contract_address: str = Field(..., min_length=10)


class ContractResponse(BaseModel):
    contractid: int
    userid: int
    contract_address: str


@router.get("/{userid}", response_model=Optional[ContractResponse])
def get_user_contract(userid: int):
    # Return the most recent contract for the user, if any
    res = (
        supabase.table("contracts")
        .select("contractid, userid, contract_address")
        .eq("userid", userid)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not res.data:
        return None
    row = res.data[0]
    return ContractResponse(
        contractid=row["contractid"],
        userid=row["userid"],
        contract_address=row["contract_address"],
    )


@router.post("/", response_model=ContractResponse)
def create_contract(payload: CreateContractRequest):
    # Insert, let DB assign contractid and created_at
    result = (
        supabase.table("contracts")
        .insert(
            {
                "userid": payload.userid,
                "contract_address": payload.contract_address.strip(),
            },
            returning="representation",
        )
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create contract")
    row = result.data[0]
    return ContractResponse(
        contractid=row["contractid"],
        userid=row["userid"],
        contract_address=row["contract_address"],
    )
