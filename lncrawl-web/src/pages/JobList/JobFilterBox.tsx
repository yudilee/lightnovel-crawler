import { Auth } from '@/store/_auth';
import { stringifyError } from '@/utils/errors';
import { PlayCircleFilled, XFilled } from '@ant-design/icons';
import { Button, Divider, Flex, Grid, message, Select, Typography } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { JobStatusFilterParams, JobTypeFilterParams } from './constants';
import type { JobListHook } from './hooks';

export const JobFilterBox: React.FC<
  Pick<JobListHook, 'type' | 'status' | 'updateParams'>
> = ({ status, type, updateParams }) => {
  const { lg } = Grid.useBreakpoint();
  const isAdmin = useSelector(Auth.select.isAdmin);
  const [isRunning, setIsRunning] = useState<boolean>();
  const [messageApi, contextHolder] = message.useMessage();

  const fetchStatus = async () => {
    try {
      const resp = await axios.get<boolean>(`/api/admin/runner/status`);
      return Boolean(resp.data);
    } catch {
      return undefined;
    }
  };

  const startRunner = async () => {
    try {
      await axios.post(`/api/admin/runner/start`);
      setIsRunning(true);
    } catch (err) {
      messageApi.open({
        type: 'error',
        content: stringifyError(err, 'Something went wrong!'),
      });
    }
  };

  const stopRunner = async () => {
    try {
      await axios.post(`/api/admin/runner/stop`);
      setIsRunning(false);
    } catch (err) {
      messageApi.open({
        type: 'error',
        content: stringifyError(err, 'Something went wrong!'),
      });
    }
  };

  useEffect(() => {
    if (!isAdmin) return;
    fetchStatus().then(setIsRunning);
    const iid = setInterval(() => {
      fetchStatus().then(setIsRunning);
    }, 5000);
    return () => clearInterval(iid);
  }, [isAdmin]);

  return (
    <Flex justify="space-between" align="center" wrap gap={5}>
      {contextHolder}

      <Flex align="center" gap={5} style={lg ? { flex: 1 } : { width: '100%' }}>
        <Typography.Text
          style={{
            textAlign: 'right',
            width: lg ? undefined : 50,
          }}
        >
          Status:
        </Typography.Text>
        <Select
          options={JobStatusFilterParams}
          defaultValue={status ?? JobStatusFilterParams[0].value}
          onChange={(status) => updateParams({ status, page: 1 })}
          style={{ flex: 1 }}
          allowClear
        />
      </Flex>

      {lg && <Divider type="vertical" />}

      <Flex align="center" gap={5} style={lg ? { flex: 1 } : { width: '100%' }}>
        <Typography.Text
          style={{
            textAlign: 'right',
            width: lg ? undefined : 50,
          }}
        >
          Type:
        </Typography.Text>
        <Select
          defaultValue={type ?? JobTypeFilterParams[0].value}
          onChange={(type) => updateParams({ type, page: 1 })}
          options={JobTypeFilterParams}
          style={{ flex: 1 }}
          allowClear
        />
      </Flex>

      {lg && <div style={{ flex: 1 }} />}

      {isAdmin && (
        <>
          {typeof isRunning === 'undefined' ? null : isRunning ? (
            <Button
              danger
              onClick={stopRunner}
              icon={<XFilled />}
              style={{ width: lg ? undefined : '100%' }}
            >
              Stop Jobs
            </Button>
          ) : (
            <Button
              type="primary"
              onClick={startRunner}
              icon={<PlayCircleFilled />}
              style={{ width: lg ? undefined : '100%' }}
            >
              Start Jobs
            </Button>
          )}
        </>
      )}
    </Flex>
  );
};
