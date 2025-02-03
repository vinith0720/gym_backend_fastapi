from fastapi import FastAPI, HTTPException,Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession,AsyncEngine
from sqlalchemy.orm import sessionmaker

from datetime import datetime,timezone


from allfunction import (
                        # function
                        get_renewal_period , check_subscription_status
                        )

from database_model import (
                            # function
                            init_session_factory,create_database,
                            # variable
                            default_async_engine,DEFAULT_DATABASE_URL,Base,Base_client,
                            # class file
                            GYM , GYMBaseModel
                            )
#_______________________________________________________________________________________________________________________________________________



async def lifespan(app: FastAPI): 
    
    async_engine_fastapi, AsyncSession_fastapi = await init_session_factory(db_name="fast_api")
    app.state.AsyncSession_fastapi = AsyncSession_fastapi
    async with async_engine_fastapi.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Create tables if not exist
       
    yield  
    await async_engine_fastapi.dispose()


app = FastAPI(lifespan=lifespan)

async def get_db() -> AsyncSession: #type:ignore
    async_session_state = app.state.AsyncSession_fastapi
    async with async_session_state() as session:
        yield session

async def get_db_common(sessionmaker: sessionmaker) -> AsyncSession: #type:ignore
    async with sessionmaker() as session:
        yield session


#________________________________________________________________________________________________________________________________________________
# INITIAL

# app.add_middleware(SessionMiddleware, secret_key="vinith")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],  
#     allow_headers=["*"],  
# )


@app.get("/gyms/")
async def read_gyms(db: AsyncSession = Depends(get_db)):
    try :
        query = select(GYM)
        result = await db.execute(query)  
        gyms = result.scalars().all()
        if not gyms:
            raise HTTPException(status_code=404,detail="no gyms found")
        return  gyms
    
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/gym/{gym_id}")
async def read_company(gym_id:int ,db: AsyncSession = Depends(get_db)):
    try:
        query = select(GYM).where(GYM.gym_id == gym_id)
        result = await db.execute(query)  
        gyms = result.scalars().all()
        if not gyms:
            raise HTTPException(status_code=404,detail="gym not found")
        
        return gyms
    
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@app.post("/creategym")
async def create_company(company_data:GYMBaseModel, db: AsyncSession = Depends(get_db)):
    try:
        query = select(GYM).where(GYM.email == company_data.email)
        result = await db.execute(query)  
        gyms = result.scalars().all()
        if not gyms:

            if company_data.subscribtion_plan is None:
                renewal:datetime =datetime.now(timezone.utc)
                company_data.subscribtion_status = False
            else:
                renewal:datetime = get_renewal_period(company_data.subscribe_date,Basicplan=company_data.subscribtion_plan)

            db_gym = GYM(   
                    name= company_data.name,
                    phone_number= company_data.phone_number,
                    email= company_data.email,
                    address= company_data.address,
                    # subscribtion_plan=company_data.subscribtion_plan,
                    # subscribtion_status= company_data.subscribtion_status,
                    # subscribe_date= company_data.subscribe_date,
                    gym_password = company_data.gym_password,

                    gym_database =company_data.name,
                    renewal_at=renewal)  
            db.add(db_gym)
            await db.commit()            
            await db.refresh(db_gym)   
            # result = await create_database(default_async_engine, db_name=db_gym.name)
            return db_gym
        else:
            await db.rollback()
            raise HTTPException(status_code=500,detail="Email is already taken")
    
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

@app.put("/gyms/{gym_id}")
async def update_gym(gym_id: int, gym_data: GYMBaseModel, db: AsyncSession = Depends(get_db)):

    try :
        query = select(GYM).where(GYM.gym_id == gym_id)
        result = await db.execute(query)
        db_gym = result.scalars().first()
    
        if not db_gym:
            raise HTTPException(status_code=404, detail="GYM not found")
        
        if gym_data.name is not None:
            db_gym.name = gym_data.name
        if gym_data.email is not None:
            db_gym.email = gym_data.email
        if gym_data.address is not None:
            db_gym.address = gym_data.address
        if gym_data.phone_number is not None:
            db_gym.phone_number =gym_data.phone_number

        if gym_data.gym_password is not None:
            db_gym.gym_password = gym_data.gym_password
        if gym_data.subscribtion_plan is not None:
            db_gym.subscribtion_plan = gym_data.subscribtion_plan
        

        if gym_data.subscribe_date is not None:
            db_gym.subscribe_date= gym_data.subscribe_date

        if (gym_data.subscribe_date is not None) and (gym_data.subscribtion_plan):
            renewal:datetime =  get_renewal_period(gym_data.subscribe_date,gym_data.subscribtion_plan)
            db_gym.renewal_at = renewal
            subscription_status = check_subscription_status(renewal_date=renewal)
            db_gym.subscribtion_status =subscription_status

        db.add(db_gym)
        await db.commit()
        await db.refresh(db_gym)
        return db_gym
    
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    

@app.delete("/del_gym")
async def del_gym_by_id(gym_id: int, db: AsyncSession = Depends(get_db)):

    try:
        
        query = select(GYM).where(GYM.gym_id == gym_id)
        result = await db.execute(query)
        gym = result.scalar_one_or_none()

        if not gym:
            raise HTTPException(status_code=404, detail="GYM not found")

        delete_query = delete(GYM).where(GYM.gym_id == gym_id)
        await db.execute(delete_query)
        await db.commit()
        # await db.execute(f"DROP DATABASE {gym.gym_database}")
        # await db.commit()
        
        return {"message": f"Gym with ID :{gym_id} and gym database : {gym.gym_database} has been deleted successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


### end company details


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
