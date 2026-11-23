export default async function csrfFetch(url, options) {
  const response = await fetch('/api/csrf-token', {
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) {
    throw new Error('Could not obtain a security token.');
  }

  const { csrf_token } = await response.json();
  const headers = new Headers(options.headers);
  headers.set('X-CSRFToken', csrf_token);
  return fetch(url, { ...options, headers, credentials: 'same-origin' });
}
