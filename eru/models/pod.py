#!/usr/bin/python
#coding:utf-8

import sqlalchemy.exc

from eru.models import db
from eru.models.base import Base
from eru.common.settings import DEFAULT_CORE_SHARE, DEFAULT_MAX_SHARE_CORE

class Pod(Base):
    __tablename__ = 'pod'

    name = db.Column(db.CHAR(30), nullable=False, unique=True)
    core_share = db.Column(db.Integer, nullable=False, default=DEFAULT_CORE_SHARE)
    max_share_core = db.Column(db.Integer, nullable=False, default=DEFAULT_MAX_SHARE_CORE)
    description = db.Column(db.Text)

    hosts = db.relationship('Host', backref='pod', lazy='dynamic')

    def __init__(self, name, description, core_share, max_share_core):
        self.name = name
        self.core_share = core_share
        self.max_share_core = max_share_core
        self.description = description

    @classmethod
    def create(cls, name, description='', core_share=DEFAULT_CORE_SHARE, max_share_core=DEFAULT_MAX_SHARE_CORE):
        try:
            pod = cls(name, description, core_share, max_share_core)
            db.session.add(pod)
            db.session.commit()
            return pod
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return None

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter(cls.name == name).first()

    def assigned_to_group(self, group):
        """这个 pod 就归这个 group 啦."""
        if not group:
            return False
        group.pods.append(self)
        db.session.add(group)
        db.session.commit()
        return True

    def get_free_public_hosts(self, limit):
        """没有被标记给 group 的 hosts"""
        from .host import Host
        return self.hosts.filter(Host.group_id == None)\
                .order_by(Host.count).limit(limit).all()

    def get_random_host(self):
        return self.hosts.limit(1).all()[0]

