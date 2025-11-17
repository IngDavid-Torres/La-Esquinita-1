
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'usuario' 
AND column_name IN ('telefono', 'telefono_verificado');

SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'sms_codes'
ORDER BY ordinal_position;

SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename IN ('usuario', 'sms_codes')
AND (indexname LIKE '%sms%' OR indexname LIKE '%telefono%');

SELECT routine_name, routine_type 
FROM information_schema.routines 
WHERE routine_name IN ('cleanup_expired_sms_codes', 'get_sms_stats', 'auto_cleanup_sms_codes');

SELECT trigger_name, event_manipulation, event_object_table
FROM information_schema.triggers 
WHERE trigger_name = 'trigger_auto_cleanup_sms';


SELECT cleanup_expired_sms_codes() as codigos_eliminados;

SELECT * FROM get_sms_stats();

SELECT phone_number, code, created_at, expires_at, attempts, used
FROM sms_codes 
WHERE expires_at > CURRENT_TIMESTAMP
ORDER BY created_at DESC;

SELECT id, nombre, email, telefono, telefono_verificado
FROM usuario 
WHERE telefono IS NOT NULL
ORDER BY telefono_verificado DESC, id DESC;
