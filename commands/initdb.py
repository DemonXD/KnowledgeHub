from utils.csession import CustomDB


def init_table(dsn: str):
    user_sql = [
        """
        DROP TABLE IF EXISTS BookingUser;
        """,
        """
        CREATE TABLE IF NOT EXISTS BookingUser(
            uid         VARCHAR(64) PRIMARY KEY NOT NULL,
            name        VARCHAR(32) NOT NULL UNIQUE,
            password    VARCHAR(128) NOT NULL,
            email       VARCHAR(128),
            mac         VARCHAR(128) DEFAULT 'None'
        );
        """,
        """
        DROP INDEX IF EXISTS user_uid_idx;
        """,
        """
        CREATE INDEX user_uid_idx ON BookingUser(uid);
        """,
        """
        DROP INDEX IF EXISTS user_name_idx;
        """,
        """
        CREATE INDEX user_name_idx ON BookingUser(name);
        """,
        """
        DROP INDEX IF EXISTS user_email_idx;
        """,
        """
        CREATE INDEX user_email_idx ON BookingUser(email);
        """,
        """
        DROP INDEX IF EXISTS user_mac_idx;
        """,
        """
        CREATE INDEX user_mac_idx ON BookingUser(mac);
        """
    ]
    note_sql = [
        """
        DROP TABLE IF EXISTS Note;
        """,
        """
        CREATE TABLE IF NOT EXISTS Note(
            uid             VARCHAR(128) NOT NULL PRIMARY KEY,
            uuid            VARCHAR(64)  NOT NULL,
            title           VARCHAR(512) NOT NULL UNIQUE,
            content         TEXT                ,
            type            VARCHAR(32)  NOT NULL,
            path            VARCHAR(512)         ,
            tag             VARCHAR(64)  NOT NULL,
            created_at      BIGINT      NOT NULL,
            modified_at     BIGINT      NOT NULL,
            is_template     SMALLINT    NOT NULL DEFAULT 0,
            is_trash        SMALLINT    NOT NULL DEFAULT 0,
            is_deleted      SMALLINT    NOT NULL DEFAULT 0
        );
        """,
        """
        DROP INDEX IF EXISTS note_uid_idx;
        """,
        """
        CREATE INDEX note_uid_idx ON Note(uid);
        """,
        """
        DROP INDEX IF EXISTS note_uuid_idx;
        """,
        """
        CREATE INDEX note_uuid_idx ON Note(uuid);
        """,
        """
        DROP INDEX IF EXISTS note_tag_idx;
        """,
        """
        CREATE INDEX note_tag_idx ON Note(tag);
        """,
        """
        DROP INDEX IF EXISTS note_title_idx;
        """,
        """
        CREATE INDEX note_title_idx ON Note(title);
        """,
        """
        DROP INDEX IF EXISTS note_created_at_idx;
        """,
        """
        CREATE INDEX note_created_at_idx ON Note(created_at);
        """,
        """
        DROP INDEX IF EXISTS note_modified_at_idx;
        """,
        """
        CREATE INDEX note_modified_at_idx ON Note(modified_at);
        """,
        """
        DROP INDEX IF EXISTS note_is_template_idx;
        """,
        """
        CREATE INDEX note_is_template_idx ON Note(is_template);
        """,
        """
        DROP INDEX IF EXISTS note_is_trash_idx;
        """,
        """
        CREATE INDEX note_is_trash_idx ON Note(is_trash);
        """,
        """
        DROP INDEX IF EXISTS note_is_deleted_idx;
        """,
        """
        CREATE INDEX note_is_deleted_idx ON Note(is_deleted);
        """
    ]

    temp_note_sql = [
        """
        DROP TABLE IF EXISTS temp_note;
        """,
        """
        CREATE TABLE IF NOT EXISTS temp_note(
            title           VARCHAR(512) NOT NULL PRIMARY KEY,
            content         TEXT ,
            is_markdown     SMALLINT    NOT NULL DEFAULT 0
        );
        """
    ]

    try:
        with CustomDB(dsn=dsn) as DB:
            for sql in user_sql:
                DB.session.execute(sql)
                DB.session.commit()

            for sql in note_sql:
                DB.session.execute(sql)
                DB.session.commit()
            
            for sql in temp_note_sql:
                DB.session.execute(sql)
                DB.session.commit()
    except Exception as e:
        print(str(e))
        DB.session.rollback()

def command():
    from conf import settings
    init_table(settings.DATABASE)