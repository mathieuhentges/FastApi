from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

from app.osv import format_requirements, post_api
import re

Base = declarative_base()


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirement = Column(Text, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "requirement": self.requirement,
            "vulnerabilities": self.get_vulnerabilities(),
            "dependencies": self.get_dependencies()
        }

    def get_dependencies(self):
        dependencies_list = []
        dependencies = self.requirement.split("\n")
        for dependency in dependencies:
            if dependency.startswith('#'):
                continue
            else:
                package = re.split(r'[=<>~!]+', dependency, maxsplit=1)
                dependencies_list.append(package[0].strip())
        return dependencies_list

    def get_vulnerabilities(self):
        return post_api("querybatch", format_requirements(self.requirement))