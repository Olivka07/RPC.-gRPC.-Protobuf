import grpc
from concurrent import futures
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from google.protobuf.empty_pb2 import Empty

import glossary_pb2
import glossary_pb2_grpc

DATABASE_URL = "sqlite:///./terms.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TermModel(Base):
    __tablename__ = "terms"
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, unique=True, index=True)
    definition = Column(String)

Base.metadata.create_all(bind=engine)


initial_terms = [
    {"term": "State Managers", "definition": "инструмент для управления глобальным хранилищем данных внутри приложения или сайта"},
    {"term": "Axios", "definition": "HTTP-клиент, основанный на Promise для node.js и браузера"},
    {"term": "Babel", "definition": "инструмент транспиляции для JavaScript"},
]


def init_db():
    db = SessionLocal()
    for term in initial_terms:
        if not db.query(TermModel).filter(TermModel.term == term["term"]).first():
            db.add(TermModel(**term))
    db.commit()
    db.close()


class DictionaryService(glossary_pb2_grpc.DictionaryServiceServicer):
    def GetAllTerms(self, request, context):
        db = SessionLocal()
        terms = db.query(TermModel).all()
        db.close()
        return glossary_pb2.TermsList(
            terms=[glossary_pb2.Term(id=t.id, term=t.term, definition=t.definition) for t in terms]
        )

    def GetTerm(self, request, context):
        db = SessionLocal()
        term = db.query(TermModel).filter(TermModel.term == request.term).first()
        db.close()
        if term:
            return glossary_pb2.GetTermResponse(
                term=glossary_pb2.Term(id=term.id, term=term.term, definition=term.definition)
            )
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Term not found")
        return glossary_pb2.GetTermResponse()

    def AddTerm(self, request, context):
        db = SessionLocal()
        new_term = TermModel(
            term=request.term.term,
            definition=request.term.definition,
        )
        db.add(new_term)
        db.commit()
        db.close()
        return glossary_pb2.AddTermResponse(message="Term added successfully!")

    def UpdateTerm(self, request, context):
        db = SessionLocal()
        term = db.query(TermModel).filter(TermModel.id == request.term.id).first()
        if term:
            term.term = request.term.term
            term.definition = request.term.definition
            db.commit()
            db.close()
            return glossary_pb2.UpdateTermResponse(message="Term updated successfully!")
        db.close()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Term not found")
        return glossary_pb2.UpdateTermResponse(message="Term not found")

    def DeleteTerm(self, request, context):
        db = SessionLocal()
        term = db.query(TermModel).filter(TermModel.id == request.id).first()  # Удаляем по ID
        if term:
            db.delete(term)
            db.commit()
            db.close()
            return glossary_pb2.DeleteTermResponse(message="Term deleted successfully!")
        db.close()
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Term not found")
        return glossary_pb2.DeleteTermResponse(message="Term not found")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    glossary_pb2_grpc.add_DictionaryServiceServicer_to_server(DictionaryService(), server)
    server.add_insecure_port("[::]:50051")
    print("gRPC server is running on port 50051")
    init_db()
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()