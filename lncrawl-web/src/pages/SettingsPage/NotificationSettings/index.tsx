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
    key: NotificationItem.FULL_NOVEL_SUCCESS,
    label: 'When full-novel available',
  },
  {
    key: NotificationItem.JOB_RUNNING,
    label: 'On any request start',
  },
  {
    key: NotificationItem.JOB_SUCCESS,
    label: 'On any request success',
  },
  {
    key: NotificationItem.JOB_FAILURE,
    label: 'On any request failure',
  },
  {
    key: NotificationItem.JOB_CANCELED,
    label: 'On any request cancel',
  },
  {
    key: NotificationItem.ARTIFACT_SUCCESS,
    label: 'When new artifact available',
  },
];

export const NotificationSettings: React.FC<any> = () => {
  const dispatch = useDispatch();
  const [messageApi, contextHolder] = message.useMessage();

  const verified = useSelector(Auth.select.isVerified);
  const notifications = useSelector(Auth.select.emailAlerts);

  const [loading, setLoading] = useState<boolean>(false);

  const updateNotification = async (item: NotificationItem, value: boolean) => {
    setLoading(true);
    try {
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
                value={notifications && notifications[key]}
                onChange={(value) => updateNotification(key, value)}
              />
            </Space>
          ),
        }))}
      />
    </Flex>
  );
};
