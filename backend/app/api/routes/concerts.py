"""Concert-related routes"""

from fastapi import APIRouter, Depends

from app.core.security import verify_bearer
from app.services.kopis import kopis_service

router = APIRouter(prefix="/api", tags=["concerts"])


@router.get("/concerts")
def get_concerts(
    stdate: str,
    eddate: str,
    cpage: int = 1,
    rows: int = 20,
    _: bool = Depends(verify_bearer),
):
    """
    KOPIS API에서 공연 목록 조회

    이 엔드포인트는 IP당 분당 50회로 요청이 제한됩니다.
    /api/token에서 발급받은 유효한 Bearer 토큰이 필요합니다.

    파라미터:
        stdate: 시작일 YYYYMMDD 형식 (예: "20250101")
        eddate: 종료일 YYYYMMDD 형식 (예: "20250131")
        cpage: 페이지 번호 (기본값: 1)
        rows: 페이지당 결과 수 (기본값: 20, 최대: 100)

    반환값:
        JSON 응답:
        - meta: 요청 메타데이터 (페이지, 행 수, 날짜, 장르)
        - raw: KOPIS의 전체 XML-to-JSON 응답
        - items: 프론트엔드 사용을 위해 정규화된 공연 항목
    """
    return kopis_service.get_concerts(
        stdate=stdate,
        eddate=eddate,
        cpage=cpage,
        rows=rows,
        shcate="CCCD"  # Currently hardcoded to popular music
    )
