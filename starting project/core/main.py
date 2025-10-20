from fastapi import FastAPI, Query, status, HTTPException,Path,Form,Body,File,UploadFile,Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from schemas import PersonCreateSchema,PersonResponseSchema,PersonUpdateSchema
from typing import List
from database import Base,engine,get_db,Person
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    yield 
    print("Application shutdown")



app = FastAPI(lifespan=lifespan)

# /names (GET(RETRIEVE),POST(CREATE))

@app.get("/names",response_model=List[PersonResponseSchema])
def retrieve_names_list(q: str | None = Query(deprecated=True,
                                              alias="search",
                                              description="it will be searched with the title you provided",
                                              example="ali",
                                              default=None,
                                              max_length=50),db:Session = Depends(get_db)):
    
    query = db.query(Person)
    if q:
        query = query.filter_by(name=q)
    result = query.all()

    return result



@app.post("/names", status_code=status.HTTP_201_CREATED,response_model=PersonResponseSchema)
def create_name(request : PersonCreateSchema,db:Session = Depends(get_db)):
    new_person = Person(name=request.name)
    db.add(new_person)
    db.commit()
    return new_person


# /names/:id (GET(RETRIEVE),PUT/PATCH(UPDATE),DELETE)
@app.get("/names/{name_id}",response_model=PersonResponseSchema)
def retrieve_name_detail(name_id: int = Path(title="object id",description="the id of the name in names_list"),db:Session = Depends(get_db)):
    person = db.query(Person).filter_by(id=name_id).one_or_none()
    if person:
        return person
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="object not found")


@app.put("/names/{name_id}", status_code=status.HTTP_200_OK,response_model=PersonResponseSchema)
def update_name_detail(request : PersonUpdateSchema,name_id: int = Path(),db:Session = Depends(get_db)):
    person = db.query(Person).filter_by(id=name_id).one_or_none()
    if person:
        person.name = request.name
        db.commit()
        db.refresh(person)
        return person
    else:   
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="object not found")


@app.delete("/names/{name_id}")
def delete_name(name_id: int,db:Session = Depends(get_db)):

    person = db.query(Person).filter_by(id=name_id).one_or_none()
    if person:        
        db.delete(person)
        db.commit()
        return JSONResponse(content={"detail": "object removed successfully"}, status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="object not found")


@app.get("/")
def root():
    content = {"message": "Hello World! "}
    return JSONResponse(content=content, status_code=status.HTTP_202_ACCEPTED)
