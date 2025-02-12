from fastapi import FastAPI

from study_planner.backend.routers.authorization import authorization_router

planner_app = FastAPI()
planner_app.include_router(authorization_router)
