
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
CREATE INDEX IF NOT EXISTS idx_usuario_telefono ON usuario(telefono);
CREATE INDEX IF NOT EXISTS idx_usuario_telefono_verificado ON usuario(telefono_verificado);

COMMIT;
