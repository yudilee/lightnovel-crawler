import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import { Auth } from '@/store/_auth';
import { stringifyError } from '@/utils/errors';
import { formatDate, parseDate } from '@/utils/time';
import {
  ClearOutlined,
  FileDoneOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { Button, Divider, Empty, Flex, message, Tabs, Typography } from 'antd';
import axios from 'axios';
import { useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { useSupportedSources } from './hooks';
import {
  defaultSourceFilters,
  SupportedSourceFilter,
} from './SupportedSourceFilter';
import { SupportedSourceList } from './SupportedSourceList';
import { filterAndSortSources } from './utils';

export const SupportedSourcesPage: React.FC<any> = () => {
  const isAdmin = useSelector(Auth.select.isAdmin);
  const [messageApi, contextHolder] = message.useMessage();
  const { data, loading, error, refresh } = useSupportedSources();

  const [tabKey, setTabKey] = useState<string>('active');
  const [filter, setFilter] = useState(defaultSourceFilters);

  const languages = useMemo(
    () => Array.from(new Set(data.map((x) => x.language))).sort(),
    [data]
  );

  const filteredSources = useMemo(
    () => filterAndSortSources(data, filter),
    [data, filter]
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
        <Typography.Title level={2}>
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
        value={filter}
        onChange={setFilter}
        languages={languages}
      />

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState
          error={error}
          title="Failed to load supported sources"
          onRetry={refresh}
        />
      ) : (
        <>
          <Tabs
            activeKey={tabKey}
            onChange={setTabKey}
            tabBarGutter={20}
            size="large"
            destroyOnHidden
            tabBarStyle={{ fontSize: 16 }}
            tabBarExtraContent={
              currentSources ? (
                <Typography.Text type="secondary" style={{ fontSize: 14 }}>
                  {currentSources.length} item
                  {currentSources.length > 1 && 's'}
                </Typography.Text>
              ) : undefined
            }
            items={[
              {
                key: 'active',
                label: 'Active Sources',
              },
              {
                key: 'used',
                label: 'Used Sources',
              },
              {
                key: 'disabled',
                label: 'Disabled Sources',
              },
            ]}
          />
          {!currentSources?.length ? (
            <Empty
              description="No sourcess"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              <Button
                shape="round"
                icon={<ClearOutlined />}
                onClick={() => setFilter(defaultSourceFilters)}
              >
                Clear Filters
              </Button>
            </Empty>
          ) : (
            <SupportedSourceList
              sources={currentSources}
              disabled={tabKey === 'disabled'}
            />
          )}
        </>
      )}
    </>
  );
};
