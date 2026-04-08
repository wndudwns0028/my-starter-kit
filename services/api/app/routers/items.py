from fastapi import APIRouter, HTTPException

from app.models.item import ItemCreate, ItemResponse

router = APIRouter(tags=["items"])

# 인메모리 저장소 (실제 프로젝트에서는 DB로 교체)
_store: dict[int, ItemResponse] = {}
_counter = 0


@router.get("/items", response_model=list[ItemResponse])
async def list_items():
  """아이템 목록 조회"""
  return list(_store.values())


@router.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(body: ItemCreate):
  """아이템 생성"""
  global _counter
  _counter += 1
  item = ItemResponse(id=_counter, **body.model_dump())
  _store[_counter] = item
  return item


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
  """아이템 단건 조회"""
  if item_id not in _store:
    raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")
  return _store[item_id]


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
  """아이템 삭제"""
  if item_id not in _store:
    raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")
  del _store[item_id]
