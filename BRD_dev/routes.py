class AppDatabaseRouter:
    app_route_label = {
        'driver': 'driver_db',
        'myapp': 'default',
    }

    def db_for_read(self, model, **hints):
        return self.app_route_label.get(
            model._meta.app_label,
            'default'
        )

    def db_for_write(self, model, **hints):
        return self.app_route_label.get(
            model._meta.app_label,
            'default'
        )

    def allow_relation(self, obj1, obj2, **hints):
        db1 = self.app_route_label.get(obj1._meta.app_label, 'default')
        db2 = self.app_route_label.get(obj2._meta.app_label, 'default')
        return db1 == db2

    def allow_migrate(self, db, app_label, **hints):
        target_db = self.app_route_label.get(
            app_label,
            'default'
        )
        return db == target_db
