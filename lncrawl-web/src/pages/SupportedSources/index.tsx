import { ErrorState } from '@/components/Loading/ErrorState';
import { LoadingState } from '@/components/Loading/LoadingState';
import { Auth } from '@/store/_auth';
import { stringifyError } from '@/utils/errors';
import { formatDate, parseDate } from '@/utils/time';
import { FileDoneOutlined, ReloadOutlined } from '@ant-design/icons';
import { Button, Divider, Flex, message, Tabs, Typography } from 'antd';
import axios from 'axios';
import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { SupportedSourceList } from './SupportedSourceList';
import { useSupportedSources } from './hooks';

export const SupportedSourcesPage: React.FC<any> = () => {
  const isAdmin = useSelector(Auth.select.isAdmin);
  const [messageApi, contextHolder] = message.useMessage();
  const { data, loading, error, refresh } = useSupportedSources();

  const active = useMemo(() => data.filter((x) => !x.is_disabled), [data]);
  const disabled = useMemo(() => data.filter((x) => x.is_disabled), [data]);

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

      <Flex align="center" justify="space-between" gap="8px" wrap>
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

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState
          error={error}
          title="Failed to load supported sources"
          onRetry={refresh}
        />
      ) : (
        <Tabs
          defaultActiveKey="active"
          tabBarGutter={20}
          size="large"
          destroyOnHidden
          tabBarStyle={{ fontSize: 16, padding: '0 10px' }}
          items={[
            {
              key: 'active',
              label: 'Active Sources',
              children: <SupportedSourceList sources={active} />,
            },
            {
              key: 'disabled',
              label: 'Disabled Sources',
              children: <SupportedSourceList sources={disabled} disabled />,
            },
          ]}
        />
      )}
    </>
  );
};
