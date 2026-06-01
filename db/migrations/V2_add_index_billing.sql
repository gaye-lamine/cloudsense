-- Cost-saving index suggested by CloudSense agent
CREATE INDEX CONCURRENTLY idx_billing_user_status 
ON billing_transactions (user_id, status);

ANALYZE billing_transactions;
