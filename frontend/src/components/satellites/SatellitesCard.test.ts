import { shallowMount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { SatelliteStatusEnum, type Satellite } from '@/lib/api/satellites/interfaces'
import SatellitesCard from './SatellitesCard.vue'

const satellite: Satellite = {
  id: '11111111-1111-1111-1111-111111111111',
  orbit_id: '22222222-2222-2222-2222-222222222222',
  name: 'Test satellite',
  description: 'Test description',
  base_url: 'https://satellite.example.com',
  paired: true,
  capabilities: {},
  present_capabilities: [],
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-02T00:00:00Z',
  last_seen_at: '2026-01-02T00:00:00Z',
  status: SatelliteStatusEnum.active,
}

describe('SatellitesCard', () => {
  it('does not present the non-clickable card as interactive', () => {
    const wrapper = shallowMount(SatellitesCard, {
      props: { data: satellite },
      global: {
        directives: { tooltip: () => undefined },
      },
    })
    const card = wrapper.get('.card')

    expect(card.element.tagName).toBe('DIV')
    expect(getComputedStyle(card.element).cursor).not.toBe('pointer')
  })
})
