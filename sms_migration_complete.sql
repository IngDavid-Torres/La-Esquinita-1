
BEGIN;

ALTER TABLE usuario 
ADD COLUMN IF NOT EXISTS telefono VARCHAR(20),
ADD COLUMN IF NOT EXISTS telefono_verificado BOOLEAN DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS sms_codes (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    attempts INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_sms_codes_phone ON sms_codes(phone_number);
CREATE INDEX IF NOT EXISTS idx_sms_codes_expires ON sms_codes(expires_at);
CREATE INDEX IF NOT EXISTS idx_sms_codes_used ON sms_codes(used);
CREATE INDEX IF NOT EXISTS idx_usuario_telefono ON usuario(telefono);
CREATE INDEX IF NOT EXISTS idx_usuario_telefono_verificado ON usuario(telefono_verificado);

CREATE OR REPLACE FUNCTION cleanup_expired_sms_codes()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sms_codes 
    WHERE expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_sms_stats()
RETURNS TABLE(
    total_codes INTEGER,
    active_codes INTEGER,
    expired_codes INTEGER,
    used_codes INTEGER,
    verified_users INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*)::INTEGER FROM sms_codes) as total_codes,
        (SELECT COUNT(*)::INTEGER FROM sms_codes WHERE used = FALSE AND expires_at > CURRENT_TIMESTAMP) as active_codes,
        (SELECT COUNT(*)::INTEGER FROM sms_codes WHERE expires_at <= CURRENT_TIMESTAMP) as expired_codes,
        (SELECT COUNT(*)::INTEGER FROM sms_codes WHERE used = TRUE) as used_codes,
        (SELECT COUNT(*)::INTEGER FROM usuario WHERE telefono_verificado = TRUE) as verified_users;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION auto_cleanup_sms_codes()
RETURNS TRIGGER AS $$
BEGIN
    
    DELETE FROM sms_codes 
    WHERE expires_at < CURRENT_TIMESTAMP - INTERVAL '1 hour';
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS trigger_auto_cleanup_sms ON sms_codes;
CREATE TRIGGER trigger_auto_cleanup_sms
    AFTER INSERT ON sms_codes
    FOR EACH ROW
    EXECUTE FUNCTION auto_cleanup_sms_codes();



COMMIT;

SELECT 'Tabla usuario actualizada' as status, 
       COUNT(*) as total_usuarios,
       COUNT(CASE WHEN telefono IS NOT NULL THEN 1 END) as usuarios_con_telefono,
       COUNT(CASE WHEN telefono_verificado = TRUE THEN 1 END) as usuarios_verificados
FROM usuario;

SELECT 'Tabla sms_codes creada' as status, 
       COUNT(*) as total_codigos
FROM sms_codes;


SELECT * FROM get_sms_stats();


SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename IN ('usuario', 'sms_codes')
AND indexname LIKE '%sms%' OR indexname LIKE '%telefono%'
ORDER BY tablename, indexname;