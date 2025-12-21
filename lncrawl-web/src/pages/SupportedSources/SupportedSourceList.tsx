import type { SourceItem } from '@/types';
import { List } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import {
  type SourceFilterState,
  SupportedSourceFilter,
} from './SupportedSourceFilter';
import { SupportedSourceItem } from './SupportedSourceItem';

export const SupportedSourceList: React.FC<{
  sources: SourceItem[];
  disabled?: boolean;
}> = ({ sources, disabled }) => {
  const [filtered, setFiltered] = useState<SourceItem[]>(sources);

  const languages = useMemo(
    () => Array.from(new Set(sources.map((x) => x.language))).sort(),
    [sources]
  );

  const applyFilters = useCallback(
    (filter: SourceFilterState) => {
      // Apply filters
      let data = [...sources];
      if (filter.language) {
        data = data.filter((src) => src.language === filter.language);
      }
      if (filter.search) {
        const search = filter.search.toLowerCase();
        data = data.filter((src) => src.domain.toLowerCase().includes(search));
      }
      if (filter.features?.length) {
        data = data.filter((src) => {
          for (const feature of filter.features) {
            if (!(src as any)[feature]) return false;
          }
          return true;
        });
      }

      // Apply sorting
      if (filter.sortBy) {
        data = [...data].sort((a, b) => {
          let aValue: number | string;
          let bValue: number | string;

          switch (filter.sortBy) {
            case 'domain':
              aValue = a.domain.toLowerCase();
              bValue = b.domain.toLowerCase();
              break;
            case 'total_novels':
              aValue = a.total_novels ?? 0;
              bValue = b.total_novels ?? 0;
              break;
            case 'feature_count':
              aValue =
                (a.has_manga ? 1 : 0) +
                (a.has_mtl ? 1 : 0) +
                (a.can_search ? 1 : 0) +
                (a.can_login ? 1 : 0);
              bValue =
                (b.has_manga ? 1 : 0) +
                (b.has_mtl ? 1 : 0) +
                (b.can_search ? 1 : 0) +
                (b.can_login ? 1 : 0);
              break;
            case 'total_commits':
              aValue = a.total_commits ?? 0;
              bValue = b.total_commits ?? 0;
              break;
            case 'version':
              aValue = a.version ?? 0;
              bValue = b.version ?? 0;
              break;
            default:
              return 0;
          }

          if (typeof aValue === 'string' && typeof bValue === 'string') {
            const comparison = aValue.localeCompare(bValue);
            return filter.sortOrder === 'asc' ? comparison : -comparison;
          } else {
            const comparison = (aValue as number) - (bValue as number);
            return filter.sortOrder === 'asc' ? comparison : -comparison;
          }
        });
      }

      setFiltered(data);
    },
    [sources]
  );

  return (
    <>
      <List
        size="small"
        header={
          <SupportedSourceFilter
            onChange={applyFilters}
            languages={languages}
          />
        }
        dataSource={filtered}
        grid={{ gutter: 5, column: 1 }}
        renderItem={(source) => (
          <List.Item style={{ margin: 0, marginTop: 5, padding: 0 }}>
            <SupportedSourceItem source={source} disabled={disabled} />
          </List.Item>
        )}
        pagination={{
          hideOnSinglePage: true,
          showSizeChanger: true,
          defaultPageSize: disabled ? 12 : 16,
          pageSizeOptions: [8, 12, 16, 25, 50, 100],
          showTotal: (total) => `Total ${total} sources`,
        }}
      />
    </>
  );
};
