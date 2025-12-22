import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import { Auth } from '@/store/_auth';
import type { SourceItem } from '@/types';
import { stringifyError } from '@/utils/errors';
import { formatDate, parseDate } from '@/utils/time';
import { FileDoneOutlined, ReloadOutlined } from '@ant-design/icons';
import { Button, Divider, Empty, Flex, Grid, message, Typography } from 'antd';
import axios from 'axios';
import { useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { useSupportedSources } from './hooks';
import { SupportedSourceFilter } from './SupportedSourceFilter';
import { SupportedSourceList } from './SupportedSourceList';
import { filterAndSortSources } from './utils';

export const SupportedSourcesPage: React.FC<any> = () => {
  const { sm } = Grid.useBreakpoint();

  const isAdmin = useSelector(Auth.select.isAdmin);
  const [messageApi, contextHolder] = message.useMessage();
  const { data, loading, error, refresh } = useSupportedSources();

  const [tabKey, setTabKey] = useState<string>('active');
  const [filteredSources, setFilteredSources] = useState<SourceItem[]>([]);

  const languages = useMemo(
    () => Array.from(new Set(data.map((x) => x.language))).sort(),
    [data]
  );

  const [activeSources, disabledSources, usedSources] = useMemo(() => {
    const active = [];
    const disabled = [];
    const used = [];
    for (const src of filteredSources) {
      if (src.is_disabled) {
        disabled.push(src);
      } else {
        active.push(src);
      }
      if (src.total_novels > 0) {
        used.push(src);
      }
    }
    return [active, disabled, used];
  }, [filteredSources]);

  const currentSources = useMemo(
    () =>
      ({
        active: activeSources,
        used: usedSources,
        disabled: disabledSources,
      }[tabKey]),
    [activeSources, disabledSources, usedSources, tabKey]
  );

  const handleUpdateSources = async () => {
    try {
      const { data } = await axios.post<string>('/api/admin/update-sources');
      const updatedAt = parseDate(Number(data) * 1000);
      messageApi.info(`Updated sources to v${data} (${formatDate(updatedAt)})`);
      refresh();
    } catch (err) {
      messageApi.error(stringifyError(err));
    }
  };

  return (
    <>
      {contextHolder}

      <Flex align="baseline" justify="space-between" gap="8px" wrap>
        <Typography.Title level={2} style={{ marginBottom: 5 }}>
          <FileDoneOutlined style={{ color: '#0f0' }} /> Supported Sources
        </Typography.Title>
        {isAdmin && (
          <Button
            shape="round"
            type="primary"
            icon={<ReloadOutlined />}
            onClick={handleUpdateSources}
          >
            Update Sources
          </Button>
        )}
      </Flex>

      <Divider size="small" />

      <SupportedSourceFilter
        languages={languages}
        onChange={(f) => setFilteredSources(filterAndSortSources(data, f))}
      />

      <Flex align="center" style={{ marginTop: 10 }}>
        <Button
          type={tabKey === 'active' ? 'primary' : 'default'}
          onClick={() => setTabKey('active')}
          style={{ borderRadius: 0, outline: 'none' }}
        >
          {sm ? 'Active Sources' : 'Active'}
        </Button>
        <Button
          type={tabKey === 'used' ? 'primary' : 'default'}
          onClick={() => setTabKey('used')}
          style={{ borderRadius: 0, outline: 'none' }}
        >
          {sm ? 'Sources In Use' : 'In Use'}
        </Button>
        <Button
          type={tabKey === 'disabled' ? 'primary' : 'default'}
          onClick={() => setTabKey('disabled')}
          style={{ borderRadius: 0, outline: 'none' }}
        >
          {sm ? 'Disabled Sources' : 'Disabled'}
        </Button>
        {currentSources?.length ? (
          <Typography.Text
            type="secondary"
            style={{
              flex: 1,
              fontSize: 14,
              marginLeft: 10,
              textAlign: 'right',
              whiteSpace: 'nowrap',
            }}
          >
            {currentSources?.length} item
            {currentSources?.length > 1 && 's'}
          </Typography.Text>
        ) : null}
      </Flex>

      <Divider size="small" style={{ marginTop: 4 }} />

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState
          error={error}
          title="Failed to load supported sources"
          onRetry={refresh}
        />
      ) : !currentSources?.length ? (
        <Empty
          description="No sources available"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      ) : (
        <SupportedSourceList
          sources={currentSources}
          disabled={tabKey === 'disabled'}
        />
      )}
    </>
  );
};
