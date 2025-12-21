import {
  BookOutlined,
  LoginOutlined,
  SearchOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  TranslationOutlined,
} from '@ant-design/icons';
import { Button, Flex, Input, Select } from 'antd';
import { sortedUniqBy } from 'lodash';
import React, { useEffect, useMemo, useState } from 'react';
import { getLanguageLabel } from './utils';

type Feature = 'has_manga' | 'has_mtl' | 'can_search' | 'can_login';
type SortBy =
  | 'domain'
  | 'total_novels'
  | 'feature_count'
  | 'total_commits'
  | 'version';
type SortOrder = 'asc' | 'desc';

const featureOptions = [
  {
    value: 'has_manga',
    label: (
      <>
        <BookOutlined /> Manga
      </>
    ),
  },
  {
    value: 'has_mtl',
    label: (
      <>
        <TranslationOutlined /> MTL
      </>
    ),
  },
  {
    value: 'can_search',
    label: (
      <>
        <SearchOutlined /> Search
      </>
    ),
  },
  {
    value: 'can_login',
    label: (
      <>
        <LoginOutlined /> Login
      </>
    ),
  },
];

export type SourceFilterState = {
  search: string;
  language?: string;
  features: Feature[];
  sortBy?: SortBy;
  sortOrder: SortOrder;
};

const defaultFilters: SourceFilterState = {
  search: '',
  language: undefined,
  features: [],
  sortBy: 'version',
  sortOrder: 'desc',
};

const defaultSortOrder: Record<SortBy, SortOrder> = {
  domain: 'asc',
  total_novels: 'desc',
  feature_count: 'desc',
  total_commits: 'desc',
  version: 'desc',
};

export const SupportedSourceFilter: React.FC<{
  value?: SourceFilterState;
  onChange: (f: SourceFilterState) => void;
  languages: string[];
}> = ({ value = defaultFilters, onChange, languages }) => {
  const [filter, setFilter] = useState<SourceFilterState>(value);

  useEffect(() => {
    const tid = setTimeout(() => onChange(filter), 50);
    return () => clearTimeout(tid);
  }, [filter, onChange]);

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

  const sortByOptions = [
    { value: 'domain', label: 'Domain' },
    { value: 'total_novels', label: 'Total Novels' },
    { value: 'feature_count', label: 'Feature Count' },
    { value: 'total_commits', label: 'Total Commits' },
    { value: 'version', label: 'Version' },
  ];

  return (
    <Flex wrap align="center" gap={5}>
      <Input
        allowClear
        prefix={<SearchOutlined />}
        placeholder="Search by URL"
        value={filter.search}
        onChange={(e) => setFilter({ ...filter, search: e.target.value })}
        style={{ width: 220 }}
      />
      <Select
        allowClear
        placeholder="Language"
        options={languageOptions}
        value={filter.language}
        onChange={(val) => setFilter({ ...filter, language: val })}
        style={{ width: 110 }}
      />
      <Select
        allowClear
        mode="multiple"
        placeholder="Features"
        style={{ minWidth: 150 }}
        value={filter.features}
        onChange={(features) => setFilter({ ...filter, features })}
        options={featureOptions}
      />
      <Select
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
        style={{ width: 160 }}
      />
      <Button onClick={() => setFilter(defaultFilters)}>Clear</Button>
    </Flex>
  );
};
