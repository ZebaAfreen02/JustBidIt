import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import MyBids from './MyBids';

jest.mock('./layout', () => function Layout({ children, notificationCount, onAlertClick }) {
  return (
    <>
      <button onClick={onAlertClick}>Open notifications ({notificationCount})</button>
      {children}
    </>
  );
});

const reply = (status, data) => ({
  status,
  ok: status >= 200 && status < 300,
  json: async () => data,
});

let originalFetch;
beforeEach(() => {
  originalFetch = global.fetch;
  localStorage.setItem('userId', '1');
});
afterEach(() => {
  localStorage.clear();
  global.fetch = originalFetch;
});

test.each([401, 403])('keeps the popup safe when bids return %s', async (status) => {
  global.fetch = jest.fn(async (url) =>
    url.includes('/bids/') ? reply(status, { error: 'Session unavailable' }) : reply(200, [{}])
  );

  render(<MyBids />);
  fireEvent.click(await screen.findByRole('button', { name: 'Open notifications (1)' }));
  expect(screen.getByText("You haven't placed any bids yet.")).toBeInTheDocument();
  expect(screen.getByRole('heading', { name: 'Notifications' })).toBeInTheDocument();
});

test('reloads for the new identity and ignores a stale response', async () => {
  let finishOldRequest;
  const oldRequest = new Promise((resolve) => { finishOldRequest = resolve; });
  global.fetch = jest.fn(async (url) => {
    if (url.endsWith('/1')) return oldRequest;
    if (url.endsWith('/2')) return reply(200, [{ product_name: 'New listing' }]);
    return reply(200, []);
  });

  const { rerender } = render(<MyBids />);
  const oldSignal = global.fetch.mock.calls[0][1].signal;
  localStorage.setItem('userId', '2');
  rerender(<MyBids />);

  await screen.findByText('New listing');
  expect(oldSignal.aborted).toBe(true);
  await act(async () => finishOldRequest(reply(200, [{ product_name: 'Old listing' }])));
  await waitFor(() => expect(screen.getByText('New listing')).toBeInTheDocument());
  expect(screen.queryByText('Old listing')).not.toBeInTheDocument();
});
