from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from database import supabase

router = APIRouter(prefix="/api/entries", tags=["entries"])


class TextEntryCreate(BaseModel):
    userid: int
    contractid: int
    entry_name: str
    encrypted_data: str
    transaction_hash: Optional[str] = None


class FileEntryCreate(BaseModel):
    userid: int
    contractid: int
    entry_name: str
    original_filename: str
    file_type: str
    file_size: int
    encrypted_cid: str
    ipfs_cid: Optional[str] = None
    transaction_hash: Optional[str] = None


class TextEntry(BaseModel):
    entryid: int
    userid: int
    contractid: int
    entry_name: str
    encrypted_data: str
    transaction_hash: Optional[str] = None


class FileEntry(BaseModel):
    entryid: int
    userid: int
    contractid: int
    entry_name: str
    original_filename: str
    file_type: str
    file_size: int
    encrypted_cid: str
    ipfs_cid: Optional[str] = None
    transaction_hash: Optional[str] = None


class StatsResponse(BaseModel):
    total_entries: int
    text_entries: int
    file_entries: int


@router.get("/stats/{userid}", response_model=StatsResponse)
def get_stats(userid: int):
    text_res = supabase.table("text_entries").select("entryid", count="exact").eq("userid", userid).execute()
    file_res = supabase.table("file_entries").select("entryid", count="exact").eq("userid", userid).execute()

    text_count = text_res.count or 0
    file_count = file_res.count or 0
    return StatsResponse(total_entries=text_count + file_count, text_entries=text_count, file_entries=file_count)


@router.get("/{userid}", response_model=List[TextEntry | FileEntry])
def list_entries(userid: int, type: Optional[Literal["text", "file"]] = Query(default=None)):
    data: list = []
    if type in (None, "text"):
        t = (
            supabase.table("text_entries")
            .select("entryid, userid, contractid, entry_name, encrypted_data, transaction_hash")
            .eq("userid", userid)
            .order("created_at", desc=True)
            .execute()
        )
        data.extend(t.data or [])
    if type in (None, "file"):
        f = (
            supabase.table("file_entries")
            .select("entryid, userid, contractid, entry_name, original_filename, file_type, file_size, encrypted_cid, ipfs_cid, transaction_hash")
            .eq("userid", userid)
            .order("created_at", desc=True)
            .execute()
        )
        data.extend(f.data or [])
    return data


@router.post("/text", response_model=TextEntry)
def create_text(payload: TextEntryCreate):
    res = (
        supabase.table("text_entries")
        .insert(
            {
                "userid": payload.userid,
                "contractid": payload.contractid,
                "entry_name": payload.entry_name,
                "encrypted_data": payload.encrypted_data,
                "transaction_hash": payload.transaction_hash,
            },
            returning="representation",
        )
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create text entry")
    return res.data[0]


@router.post("/file", response_model=FileEntry)
def create_file(payload: FileEntryCreate):
    res = (
        supabase.table("file_entries")
        .insert(
            {
                "userid": payload.userid,
                "contractid": payload.contractid,
                "entry_name": payload.entry_name,
                "original_filename": payload.original_filename,
                "file_type": payload.file_type,
                "file_size": payload.file_size,
                "encrypted_cid": payload.encrypted_cid,
                "ipfs_cid": payload.ipfs_cid,
                "transaction_hash": payload.transaction_hash,
            },
            returning="representation",
        )
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create file entry")
    return res.data[0]
