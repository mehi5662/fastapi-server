from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Text, DateTime,Table,UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
from sqlalchemy.orm import backref

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# for postgres or other relational databases
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver:5432/db"
# SQLALCHEMY_DATABASE_URL = "mysql://username:password@localhost/db_name"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False  # only for sqlite
                  }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# create base class for declaring tables
Base = declarative_base()


enrollments = Table("enrollments",Base.metadata,
                    Column("id",Integer, primary_key=True, autoincrement=True),
                    Column("user_id",Integer, ForeignKey("users.id")),
                    Column("course_id",Integer, ForeignKey("courses.id")),
                    Column("enrolled_date",DateTime(), default=datetime.now),
                    UniqueConstraint("user_id","course_id",name="unique_user_course_enrolled")
                    )



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30))
    email = Column(String())
    password = Column(String())
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    addresses = relationship("Address", backref="user")
    posts = relationship("Post", backref="user")

    profile = relationship("Profile", backref="user", uselist=False)
    courses = relationship("Course",secondary=enrollments,back_populates="attendees")


    def __repr__(self):
        return f"User(id={self.id},username={self.username},email={self.email})"


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    city = Column(String())
    state = Column(String())
    zip_code = Column(String())

    def __repr__(self):
        return f"Address(id={self.id},user_id={self.user_id},city={self.city})"


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    first_name = Column(String())
    last_name = Column(String())
    bio = Column(Text(), nullable=True)

    def __repr__(self):
        return f"Profile(id={self.id},first_name={self.first_name},last_name={self.last_name})"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String())
    content = Column(Text())

    comments = relationship("Comment", backref="post")

    created_date = Column(DateTime(), default=datetime.now)
    updated_date = Column(
        DateTime(), default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"Post(id={self.id},title={self.title})"


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    # parent = relationship("Comment",back_populates="children",remote_side=[id])
    children = relationship(
        "Comment", backref=backref("parent", remote_side=[id]))

    content = Column(Text())
    created_date = Column(DateTime(), default=datetime.now)

    def __repr__(self):
        return f"Comment(id={self.id},post_id={self.post_id},user_id={self.user_id},parent_id={self.parent_id})"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String())
    description = Column(Text())

    created_date = Column(DateTime(), default=datetime.now)
    
    attendees = relationship("User",secondary=enrollments,back_populates="courses")


    def __repr__(self):
        return f"Course(id={self.id},title={self.title})"


# to create tables and database
Base.metadata.create_all(engine)

session = SessionLocal()

user = session.query(User).filter_by(username="alibigdeli").one_or_none()
course = session.query(Course).filter_by(title="Python").one()

print(user.courses)