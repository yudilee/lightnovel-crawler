import { Favicon } from '@/components/Favicon';
import { Flex, Input, message, Select, Space } from 'antd';
import axios from 'axios';
import { useEffect, useMemo, useState } from 'react';
import type { SourceItem } from '../../types';
import { type NovelListHook } from './hooks';

export const NovelFilterBox: React.FC<
  Pick<NovelListHook, 'search' | 'domain' | 'updateParams'>
> = ({ search: initialSearch, domain: initialDomain, updateParams }) => {
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState<SourceItem[]>([]);

  useEffect(() => {
    const loadSources = async () => {
      try {
        setLoading(true);
        const { data } = await axios.get<SourceItem[]>('/api/novel/sources');
        setSources(data);
      } catch {
        message.error('Failed to load sources');
      } finally {
        setLoading(false);
      }
    };
    loadSources();
  }, []);

  const sourceOptions = useMemo(() => {
    return sources.map((source) => ({
      value: source.domain,
      label: (
        <Space key={source.domain}>
          <Favicon url={source.url} /> {source.domain}
        </Space>
      ),
    }));
  }, [sources]);

  return (
    <Flex align="center" justify="space-between" gap="8px" wrap>
      {/* Domain Select */}
      <Select
        loading={loading}
        defaultValue={initialDomain || undefined}
        onChange={(value) => updateParams({ domain: value || '', page: 1 })}
        placeholder="Select a domain"
        allowClear
        size="large"
        options={sourceOptions}
        style={{ flex: 1, minWidth: 250 }}
      />

      {/* Search Input */}
      <Input.Search
        defaultValue={initialSearch}
        onSearch={(search) => updateParams({ search, page: 1 })}
        placeholder="Search novels"
        allowClear
        size="large"
        style={{ flex: 3, minWidth: 300 }}
      />
    </Flex>
  );
};
