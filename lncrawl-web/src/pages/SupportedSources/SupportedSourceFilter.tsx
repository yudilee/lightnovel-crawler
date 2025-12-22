import {
  BookOutlined,
  LoginOutlined,
  SearchOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  TranslationOutlined,
} from '@ant-design/icons';
import { Flex, Input, Select } from 'antd';
import { sortedUniqBy } from 'lodash';
import React, { useMemo } from 'react';
import { getLanguageLabel } from './utils';

type Feature = 'has_manga' | 'has_mtl' | 'can_search' | 'can_login';
type SortBy = 'domain' | 'total_novels' | 'total_commits' | 'version';
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

export const defaultSourceFilters: SourceFilterState = {
  search: '',
  language: undefined,
  features: [],
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
  value: SourceFilterState;
  onChange: (f: SourceFilterState) => void;
  languages: string[];
}> = ({ value: filter, onChange: setFilter, languages }) => {
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

      {/* Feature filter */}
      <Select
        virtual={false}
        allowClear
        mode="multiple"
        placeholder="Features"
        style={{ flex: 1, minWidth: 150 }}
        value={filter.features}
        onChange={(features) => setFilter({ ...filter, features })}
        options={featureOptions}
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
    </Flex>
  );
};
