from neo4j.v1 import GraphDatabase, basic_auth, SessionError, TransactionError


class Db:
    driver = None

    def __init__(self):
        Db.driver = GraphDatabase.driver("bolt://hobby-pdljabkaedndgbkecaicgaal.dbs.graphenedb.com:24786",
                                            auth=basic_auth("onmyoji", "b.sqptQQ3tGf9c.cJz5sPNcHJTXyU8k"))

    def close(self):
        self.driver.close()

    @staticmethod
    def run(*args, **kwargs):
        if Db.driver is None:
            db = Db()
            Db.driver = db.driver

        try:
            return Db.driver.session().run(*args, **kwargs)
        except SessionError:
            return False
