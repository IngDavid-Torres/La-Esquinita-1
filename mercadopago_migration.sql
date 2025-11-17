
ALTER TABLE pedido 
ADD COLUMN IF NOT EXISTS nombre VARCHAR(200),
ADD COLUMN IF NOT EXISTS correo VARCHAR(200),
ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(100),
ADD COLUMN IF NOT EXISTS payment_id VARCHAR(200);

CREATE INDEX IF NOT EXISTS idx_pedido_payment_id ON pedido(payment_id);
CREATE INDEX IF NOT EXISTS idx_pedido_metodo_pago ON pedido(metodo_pago);
CREATE INDEX IF NOT EXISTS idx_pedido_estado ON pedido(estado);


UPDATE pedido 
SET metodo_pago = 'Tarjeta' 
WHERE metodo_pago IS NULL;

COMMIT;