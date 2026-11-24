import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';

// Only these status codes count as "expected". Without this, every intentional
// 400 (out of stock) would be reported as a failed request in the summary.
http.setResponseCallback(http.expectedStatuses(201, 400));

const accepted = new Counter('orders_accepted');
const rejected = new Counter('orders_rejected');
const unexpected = new Counter('orders_unexpected');

export const options = {
  scenarios: {
    checkout: {
      executor: 'per-vu-iterations',
      vus: Number(__ENV.VUS || 20),
      iterations: 1,
      maxDuration: '60s',
    },
  },
  thresholds: {
    // Any 5xx or network error fails the run.
    orders_unexpected: ['count==0'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const PRODUCT_ID = Number(__ENV.PRODUCT_ID || 1);

export default function () {
  const payload = JSON.stringify({
    product_id: PRODUCT_ID,
    quantity: 1,
    customer_email: 'loadtest@example.com',
  });

  const res = http.post(`${BASE_URL}/api/orders/`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  if (res.status === 201) {
    accepted.add(1);
  } else if (res.status === 400) {
    rejected.add(1);
  } else {
    unexpected.add(1);
  }

  check(res, {
    'status is 201 (accepted) or 400 (rejected)':
      (r) => r.status === 201 || r.status === 400,
  });
}
