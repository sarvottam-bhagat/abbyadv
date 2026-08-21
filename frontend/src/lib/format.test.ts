import { describe, expect, it } from 'vitest';
import { initials } from './format';

describe('initials', () => {
  it('returns two readable initials for a client name', () => {
    expect(initials('Asha Verma')).toBe('AV');
  });
});
