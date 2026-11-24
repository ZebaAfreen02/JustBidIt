import { fireEvent, render, screen } from '@testing-library/react';
import { useForm } from 'react-hook-form';
import ManageAuctions from './custManageAuctions';
import ResetPassword from './resetPassword';
import SignupForm from './signup';

jest.mock('react-hook-form', () => ({ useForm: jest.fn() }));

test('the auction table and detail use Highest Bidder and retain N/A', async () => {
  const originalFetch = global.fetch;
  global.fetch = jest.fn(async () => ({
    json: async () => ({
      status: 'success',
      auctions: [{ id: 1, name: 'Demo phone', price: 10, seller: 'N/A' }],
    }),
  }));
  try {
    render(<ManageAuctions />);
    expect(screen.getByRole('columnheader', { name: 'Highest Bidder' })).toBeInTheDocument();
    await screen.findByText('Demo phone');
    expect(screen.getByText('N/A')).toBeInTheDocument();
    fireEvent.click(screen.getByTitle('View'));
    const details = await screen.findByRole('dialog');
    expect(details).toHaveTextContent('Highest Bidder: N/A');
  } finally {
    global.fetch = originalFetch;
  }
});

test('reset and signup keep the same validation decisions', () => {
  const rules = {};
  useForm.mockReturnValue({
    register: (name, options) => {
      rules[name] = options;
      return { name };
    },
    handleSubmit: () => () => {},
    watch: () => 'Strong1!',
    formState: { errors: {}, touchedFields: {} },
  });

  const { unmount } = render(<ResetPassword />);
  expect(rules.password.validate('Strong1!')).toBe(true);
  for (const value of ['strongpass!', '12345678!', 'Strong123']) {
    expect(rules.password.validate(value)).toBe('Must include a letter, number, and special character');
  }
  unmount();

  render(<SignupForm />);
  expect(rules.confirmPassword.validate('Strong1!')).toBe(true);
  expect(rules.confirmPassword.validate('Different1!')).toBe('Passwords must match and meet strength rules');
});
