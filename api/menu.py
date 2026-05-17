from fastapi import APIRouter, Depends

from api.dependencies.auth import get_current_user
from models.user import User
from schemas.common import Response

router = APIRouter()


def _dashboard_menus() -> list[dict[str, object]]:
    return [
        {
            "name": "Dashboard",
            "path": "/dashboard",
            "redirect": "/analytics",
            "component": "BasicLayout",
            "meta": {
                "icon": "lucide:layout-dashboard",
                "order": -1,
                "title": "page.dashboard.title",
            },
            "children": [
                {
                    "name": "Analytics",
                    "path": "/analytics",
                    "component": "/dashboard/analytics/index",
                    "meta": {
                        "affixTab": True,
                        "icon": "lucide:area-chart",
                        "title": "page.dashboard.analytics",
                    },
                },
                {
                    "name": "Workspace",
                    "path": "/workspace",
                    "component": "/dashboard/workspace/index",
                    "meta": {
                        "icon": "carbon:workspace",
                        "title": "page.dashboard.workspace",
                    },
                },
            ],
        }
    ]


@router.get("/all", response_model=Response[list[dict[str, object]]], summary="获取用户菜单")
async def get_all_menus(_current_user: User = Depends(get_current_user)) -> Response[list[dict[str, object]]]:
    return Response.ok(data=_dashboard_menus())
