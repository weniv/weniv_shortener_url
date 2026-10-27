-- weniv.link 앱 전용 DB 계정(shortener_app)에 shortener DB를 넘긴다. 비밀번호는 여기 두지 않는다.
-- 먼저 역할을 만든다 (슈퍼유저·DB 만들기·역할 만들기 권한 없음):
--   CREATE ROLE shortener_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS
--     CONNECTION LIMIT 20 PASSWORD '<새 비밀번호>';
-- 그다음: psql -U postgres -d shortener -v ON_ERROR_STOP=1 -f app-db-role.sql
-- 앱이 마이그레이션도 하므로 shortener DB와 그 안의 테이블·시퀀스를 이 계정이 소유한다. 다른 DB는 건드리지 않는다.
-- 되돌리기: ALTER DATABASE shortener OWNER TO postgres; (shortener DB에서) REASSIGN OWNED BY shortener_app TO postgres;
--   GRANT CONNECT, TEMPORARY ON DATABASE shortener TO PUBLIC; DROP OWNED BY shortener_app; 다른 DB에서 연결이 없으면 DROP ROLE shortener_app;
BEGIN;

ALTER DATABASE shortener OWNER TO shortener_app;

-- PG15+에서 public 스키마는 pg_database_owner 소유라 DB 소유자가 곧 스키마 소유자다.
DO $$
DECLARE r record;
BEGIN
  -- 테이블을 먼저 넘기면 테이블에 딸린(serial/identity) 시퀀스도 함께 넘어간다
  FOR r IN SELECT n.nspname, c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p', 'f') LOOP
    EXECUTE format('ALTER TABLE %I.%I OWNER TO shortener_app', r.nspname, r.relname);
  END LOOP;
  FOR r IN SELECT n.nspname, c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = 'public' AND c.relkind IN ('v', 'm') LOOP
    EXECUTE format('ALTER TABLE %I.%I OWNER TO shortener_app', r.nspname, r.relname);
  END LOOP;
  FOR r IN SELECT n.nspname, c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = 'public' AND c.relkind = 'S'
             AND c.relowner <> 'shortener_app'::regrole LOOP
    EXECUTE format('ALTER SEQUENCE %I.%I OWNER TO shortener_app', r.nspname, r.relname);
  END LOOP;
END $$;

-- 다른 일반 계정이 이 DB에 붙지 못하게 한다 (슈퍼유저 postgres는 그대로 붙는다)
REVOKE CONNECT, TEMPORARY ON DATABASE shortener FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE shortener TO shortener_app;

COMMIT;

-- 확인: shortener_app이 아닌 소유자가 남았는지 (0줄이어야 한다)
SELECT c.relkind, c.relname, pg_get_userbyid(c.relowner) AS owner
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f')
  AND c.relowner <> 'shortener_app'::regrole;
