import type { SourceItem } from '@/types';
import type { SourceFilterState } from './SupportedSourceFilter';

/**
 * Get the language label for a language code
 * @param lang - The language code
 * @returns The language label
 */
export function getLanguageLabel(lang?: string): string {
  if (!lang || lang.length !== 2) {
    return 'Any';
  }
  const names = new Intl.DisplayNames(['en'], {
    type: 'language',
  });
  return names.of(lang) || '';
}

/**
 * Filter and sort sources based on the filter state
 * @param sources - The sources to filter and sort
 * @param filter - The filter state
 * @returns The filtered and sorted sources
 */
export function filterAndSortSources(
  sources: SourceItem[],
  filter: SourceFilterState
): SourceItem[] {
  const { language, search, features, sortBy, sortOrder } = filter;
  let data = [...sources];

  // Apply filters
  const searchLower = search?.trim().toLowerCase();
  if (language || searchLower || Object.values(features).some(Boolean)) {
    data = data.filter((src) => {
      if (language && src.language !== language) {
        return false;
      }
      if (searchLower && !src.domain.toLowerCase().includes(searchLower)) {
        return false;
      }
      if (features.has_manga && !src.has_manga) {
        return false;
      }
      if (features.has_mtl && !src.has_mtl) {
        return false;
      }
      if (features.can_search && !src.can_search) {
        return false;
      }
      if (features.can_login && !src.can_login) {
        return false;
      }
      return true;
    });
  }

  // Apply sorting
  if (sortBy) {
    data = [...data].sort((a, b) => {
      let comparison: number;

      switch (sortBy) {
        case 'domain':
          comparison = a.domain.localeCompare(b.domain);
          break;
        case 'total_novels':
          comparison = (a.total_novels ?? 0) - (b.total_novels ?? 0);
          break;
        case 'total_commits':
          comparison = (a.total_commits ?? 0) - (b.total_commits ?? 0);
          break;
        case 'version':
          comparison = (a.version ?? 0) - (b.version ?? 0);
          break;
        default:
          return 0;
      }

      return sortOrder === 'desc' ? -comparison : comparison;
    });
  }

  return data;
}
