import {
  BookOutlined,
  ClearOutlined,
  LoginOutlined,
  SearchOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  TranslationOutlined,
} from '@ant-design/icons';
import { Button, Flex, Input, Select, Space } from 'antd';
import { isEqual, sortedUniqBy } from 'lodash';
import React, { useEffect, useMemo, useState } from 'react';
import { getLanguageLabel } from './utils';

type SortBy = 'domain' | 'total_novels' | 'total_commits' | 'version';
type SortOrder = 'asc' | 'desc';

export type SourceFilterState = {
  search: string;
  language?: string;
  features: {
    has_manga?: boolean;
    has_mtl?: boolean;
    can_search?: boolean;
    can_login?: boolean;
  };
  sortBy?: SortBy;
  sortOrder: SortOrder;
};

const defaultSourceFilters: SourceFilterState = {
  search: '',
  language: undefined,
  features: {},
  sortBy: 'version',
  sortOrder: 'desc',
};

const defaultSortOrder: Record<SortBy, SortOrder> = {
  domain: 'asc',
  total_novels: 'desc',
  total_commits: 'desc',
  version: 'desc',
};

export const SupportedSourceFilter: React.FC<{
  onChange: (f: SourceFilterState) => void;
  languages: string[];
}> = ({ onChange, languages }) => {
  const [filter, setFilter] = useState(defaultSourceFilters);

  useEffect(() => {
    const timeout = setTimeout(() => {
      onChange(filter);
    }, 50);
    return () => clearTimeout(timeout);
  }, [filter, onChange]);

  const sortByOptions = [
    { value: 'domain', label: 'Domain' },
    { value: 'total_novels', label: 'Total Novels' },
    { value: 'total_commits', label: 'Total Commits' },
    { value: 'version', label: 'Version' },
  ];

  const languageOptions = useMemo(() => {
    const options = languages
      .map((lang) => ({
        value: lang,
        label: getLanguageLabel(lang),
      }))
      .filter((x) => x.label !== '')
      .sort((a, b) => a.label!.localeCompare(b.label!));
    return sortedUniqBy(options, 'label');
  }, [languages]);

  const toggleFeature = (feature: keyof SourceFilterState['features']) => {
    setFilter((prev) => ({
      ...prev,
      features: {
        ...prev.features,
        [feature]: !prev.features[feature],
      },
    }));
  };

  return (
    <Flex align="center" gap={5} wrap>
      {/* Search */}
      <Input
        allowClear
        prefix={<SearchOutlined />}
        placeholder="Search by URL"
        value={filter.search}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
          setFilter({ ...filter, search: e.target.value })
        }
        style={{ flex: 2, minWidth: 250 }}
      />

      {/* Sort */}
      <Select
        virtual={false}
        placeholder="Sort by"
        options={sortByOptions}
        value={filter.sortBy}
        prefix={
          filter.sortOrder === 'asc' ? (
            <SortAscendingOutlined />
          ) : (
            <SortDescendingOutlined />
          )
        }
        onClear={() => {
          setFilter({
            ...filter,
            sortBy: 'version',
            sortOrder: 'desc',
          });
        }}
        onSelect={(value) => {
          if (filter.sortBy === value) {
            setFilter({
              ...filter,
              sortOrder: filter.sortOrder === 'asc' ? 'desc' : 'asc',
            });
          } else {
            setFilter({
              ...filter,
              sortBy: value,
              sortOrder: defaultSortOrder[value],
            });
          }
        }}
        allowClear={filter.sortBy !== 'version' || filter.sortOrder !== 'desc'}
        style={{ flex: 1, minWidth: 150 }}
      />

      {/* Language filter */}
      <Select
        virtual={false}
        allowClear
        placeholder="Language"
        options={languageOptions}
        value={filter.language}
        onChange={(val) => setFilter({ ...filter, language: val })}
        style={{ flex: 1, minWidth: 150 }}
      />

      {/* Feature filters */}
      <Space size={0} wrap>
        <Button
          type={filter.features.has_manga ? 'primary' : 'default'}
          onClick={() => toggleFeature('has_manga')}
          icon={<BookOutlined />}
          style={{ outline: 'none', borderRadius: 0 }}
        >
          Manga
        </Button>
        <Button
          type={filter.features.has_mtl ? 'primary' : 'default'}
          onClick={() => toggleFeature('has_mtl')}
          icon={<TranslationOutlined />}
          style={{ outline: 'none', borderRadius: 0 }}
        >
          MTL
        </Button>
        <Button
          type={filter.features.can_search ? 'primary' : 'default'}
          onClick={() => toggleFeature('can_search')}
          icon={<SearchOutlined />}
          style={{ outline: 'none', borderRadius: 0 }}
        >
          Search
        </Button>
        <Button
          type={filter.features.can_login ? 'primary' : 'default'}
          onClick={() => toggleFeature('can_login')}
          icon={<LoginOutlined />}
          style={{ outline: 'none', borderRadius: 0 }}
        >
          Login
        </Button>
      </Space>

      {/* Clear Filters */}
      {!isEqual(filter, defaultSourceFilters) && (
        <Button
          shape="round"
          icon={<ClearOutlined />}
          onClick={() => setFilter(defaultSourceFilters)}
        />
      )}
    </Flex>
  );
};
