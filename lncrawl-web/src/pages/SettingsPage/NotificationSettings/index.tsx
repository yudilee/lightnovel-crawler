import { Auth } from '@/store/_auth';
import { NotificationItem } from '@/types';
import { stringifyError } from '@/utils/errors';
import {
  Alert,
  Descriptions,
  Flex,
  message,
  Space,
  Switch,
  Typography,
} from 'antd';
import axios from 'axios';
import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

const items = [
  {
    key: NotificationItem.NOVEL_SUCCESS,
    label: 'On novel fetch request success',
  },
  {
    key: NotificationItem.ARTIFACT_SUCCESS,
    label: 'On artifact create request success',
  },
  {
    key: NotificationItem.JOB_RUNNING,
    label: 'When any request starts running',
  },
  {
    key: NotificationItem.JOB_SUCCESS,
    label: 'When any request is successful',
  },
  {
    key: NotificationItem.JOB_FAILURE,
    label: 'When any request failed',
  },
  {
    key: NotificationItem.JOB_CANCELED,
    label: 'When any request canceled',
  },
];

export const NotificationSettings: React.FC<any> = () => {
  const dispatch = useDispatch();
  const [messageApi, contextHolder] = message.useMessage();

  const verified = useSelector(Auth.select.isVerified);
  const notifications = useSelector(Auth.select.emailAlerts);

  const [loading, setLoading] = useState<boolean>(false);

  const toggleNotification = async (item: NotificationItem) => {
    setLoading(true);
    try {
      const value = !(notifications && notifications[item]);
      const update = { ...notifications, [item]: value };
      await axios.put(`/api/settings/notifications`, { email_alerts: update });
      dispatch(Auth.action.updateEmailAlertConfig(update));
    } catch (err) {
      messageApi.error(stringifyError(err, 'Failed to update notification'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex vertical gap={5}>
      {contextHolder}

      {!verified && (
        <Alert
          showIcon
          type="warning"
          message="Please verify your email first to get notifications."
        />
      )}

      <Typography.Text type="secondary" style={{ fontSize: 12 }}>
        You will be notified by email on these events:
      </Typography.Text>

      <Descriptions
        bordered
        column={1}
        size="small"
        styles={{ label: { width: 275 } }}
        items={items.map(({ key, label }) => ({
          key,
          label,
          children: (
            <Space size="small">
              <Switch
                loading={loading}
                disabled={!verified}
                onClick={() => toggleNotification(key)}
                checked={Boolean(notifications && notifications[key])}
              />
            </Space>
          ),
        }))}
      />
    </Flex>
  );
};
