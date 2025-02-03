from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession,AsyncEngine
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import Column, Integer, String,DateTime,ForeignKey,Boolean,text

from pydantic import BaseModel,EmailStr
from datetime import datetime,timezone

#_______________________________________________________________________________________________________________________________________________


### for database connection

Base = declarative_base()
Base_client = declarative_base()
DEFAULT_DATABASE_URL = "mysql+aiomysql://root:@localhost/"
default_async_engine = create_async_engine(DEFAULT_DATABASE_URL, echo=True)


async def create_database(async_engine: AsyncEngine, db_name: str):

    async with async_engine.connect() as connection:
        await connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))
    return f"Database '{db_name}' created successfully."



async def init_session_factory(db_name: str):

    result = await create_database(default_async_engine, db_name)

    DATABASE_URL = DEFAULT_DATABASE_URL + db_name

    async_engine = create_async_engine(DATABASE_URL, echo=True)

    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )
    return async_engine, AsyncSessionLocal


#__________________________________________________________________________________________________________________________________________________________

### for models code 

# company

class GYM(Base):
    __tablename__ = "tbl_gym_lists"

    gym_id:int =Column(Integer,primary_key=True,index=True)

    name:str = Column(String(length=100),unique=True)
    phone_number:int = Column(Integer,unique=True,nullable=False)
    email:EmailStr =Column(String(length=50),unique=True,nullable=False)
    address:str = Column(String(length=255))

    create_at:DateTime = Column(DateTime,default=datetime.now(timezone.utc))
    subscribtion_plan =Column(String(length=10))
    subscribe_date:DateTime = Column(DateTime,default=datetime.now(timezone.utc))
    subscribtion_status =Column(Boolean,default=False)
    renewal_at:DateTime =Column(DateTime,default=datetime.now(timezone.utc))

    gym_database:str =Column(String(length=100),unique=True)
    gym_password:str = Column(String(length=100))


class GYMBaseModel(BaseModel):
    
    name:str|None =None
    phone_number:int|None = None
    email:EmailStr|None = None
    address:str|None = None
    subscribtion_plan:str|None =None
    subscribtion_status:bool|None = None
    subscribe_date: datetime|None = None
    gym_password:str|None = None

#______________________________________________________________________________________________________________________________________________________
# Branch

# class Branch(Base_client):
#     __table__ ="tbl_branch_list"

#     admin_id:int = Column(Integer,index=True)

#     branch_id:int = Column(Integer,primary_key=True,index=True)
#     branch_name:str =Column(String(length=100))
#     branch_address:str =Column(String(length=250))
#     branch_phone:int = Column(Integer,unique=True,nullable=False)
#     branch_email:EmailStr =Column(String(length=50),unique=True,nullable=False) 
#     branch_create_at:DateTime = Column(DateTime,default=datetime.now)


# class BranchBaseModel(BaseModel):
        
#     admin_id:int|None = None

#     branch_id:int | None = None
#     branch_name:str | None = None
#     branch_address:str | None = None
#     branch_phone:int | None = None
#     branch_email:EmailStr | None = None
#     branch_create_at:DateTime | None = None
        

#____________________________________________________________________________________________________________________________________________________



# # Customer

# class Customer(Base):
#     __tablename__ = "tbl_customer"

#     id:int = Column(Integer, primary_key=True, index=True)
#     name:str = Column(String(length=255))
#     age:int = Column(Integer)
#     membership_type:str = Column(String(length=255),default="BASIC")
#     subscribe_date:datetime = Column(DateTime)
#     renewal_date:datetime = Column(DateTime)

# class CustomerBaseModel(BaseModel):

#     name:str|None = None
#     age:int|None = None
#     membership_type:str|None =None
#     subscribe_date:datetime|None = None

#__________________________________________________________________________________________________________________________________________________
