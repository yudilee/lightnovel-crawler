import { Auth } from '@/store/_auth';
import { ReloadOutlined } from '@ant-design/icons';
import {
  Button,
  Flex,
  message,
  Result,
  Space,
  Spin,
  Tabs,
  Typography,
} from 'antd';
import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { SupportedSourceList } from './SupportedSourceList';
import { useSupportedSources } from './hooks';
import { stringifyError } from '@/utils/errors';
import axios from 'axios';
import { formatDate, parseDate } from '@/utils/time';

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

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load novel list"
          subTitle={error}
          extra={[<Button onClick={refresh}>Retry</Button>]}
        />
      </Flex>
    );
  }
  return (
    <>
      {contextHolder}
      <Tabs
        defaultActiveKey="active"
        style={{ padding: 15 }}
        tabBarGutter={20}
        tabBarExtraContent={
          isAdmin && (
            <Button
              shape="round"
              type="primary"
              icon={<ReloadOutlined />}
              onClick={handleUpdateSources}
            >
              Update Sources
            </Button>
          )
        }
      >
        <Tabs.TabPane
          key="active"
          tab={
            <Space>
              <Typography.Text strong>Active Sources</Typography.Text>
              <small>
                <code>{active.length}</code>
              </small>
            </Space>
          }
        >
          <SupportedSourceList sources={active} />
        </Tabs.TabPane>
        <Tabs.TabPane
          key="disabled"
          tab={
            <Space>
              <Typography.Text strong>Disabled Sources</Typography.Text>
              <small>
                <code>{disabled.length}</code>
              </small>
            </Space>
          }
        >
          <SupportedSourceList sources={disabled} disabled />
        </Tabs.TabPane>
      </Tabs>
    </>
  );
};
