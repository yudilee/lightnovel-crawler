import { Auth } from '@/store/_auth';
import type { Library, User } from '@/types';
import { stringifyError } from '@/utils/errors';
import {
  Button,
  Card,
  Flex,
  Result,
  Space,
  Spin,
  Switch,
  Tag,
  Typography,
  message,
} from 'antd';
import axios from 'axios';
import { useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import { UserDetailsCard } from '../JobDetails/UserDetailsCard';
import { LibraryNovelList } from './NovelList';

export const LibraryDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const user = useSelector(Auth.select.user);
  const isAdmin = useSelector(Auth.select.isAdmin);
  const [messageApi, contextHolder] = message.useMessage();

  const [loading, setLoading] = useState<boolean>(true);
  const [refresh, setRefresh] = useState<number>(0);
  const [error, setError] = useState<string>();
  const [owner, setOwner] = useState<User>();
  const [library, setLibrary] = useState<Library>();

  const isOwner = useMemo(
    () => Boolean(library && user?.id === library.user_id),
    [user?.id, library]
  );

  useEffect(() => {
    const loadDetails = async () => {
      setLoading(true);
      setError(undefined);
      try {
        const { data } = await axios.get<Library>(`/api/library/${id}`);
        setLibrary(data);
      } catch (err) {
        setError(stringifyError(err));
      } finally {
        setLoading(false);
      }
    };
    if (id) {
      loadDetails();
    }
  }, [id, refresh, messageApi]);

  useEffect(() => {
    const loadOwner = async () => {
      try {
        const { data } = await axios.get<User>(`/api/user/${library?.user_id}`);
        setOwner(data);
      } catch (err) {
        messageApi.error(stringifyError(err));
      }
    };
    if (library?.user_id && isAdmin) {
      loadOwner();
    }
  }, [library?.user_id, isAdmin, messageApi]);

  const handleTogglePublic = async (checked: boolean) => {
    if (!id) return;
    try {
      await axios.patch(`/api/library/${id}`, { is_public: checked });
      setLibrary((library) => library && { ...library, is_public: checked });
      messageApi.success(`Library is now ${checked ? 'public' : 'private'}`);
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

  if (error || !library) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load novel list"
          subTitle={error}
          extra={[
            <Button onClick={() => setRefresh((v) => v + 1)}>Retry</Button>,
          ]}
        />
      </Flex>
    );
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      {contextHolder}

      <Card>
        <Flex align="center" justify="space-between" wrap>
          <Space align="center">
            <Typography.Title level={3} style={{ margin: 0 }}>
              {library.name || 'Library'}
            </Typography.Title>
            <Tag color={library.is_public ? 'green' : 'blue'}>
              {library.is_public ? 'Public' : 'Private'}
            </Tag>
          </Space>
          {isOwner && (
            <Space align="center">
              <Typography.Text>Public</Typography.Text>
              <Switch
                checked={library.is_public}
                onChange={handleTogglePublic}
                disabled={loading}
              />
            </Space>
          )}
        </Flex>
        <Typography.Paragraph type="secondary">
          {library.description || 'No description'}
        </Typography.Paragraph>
      </Card>

      {owner && <UserDetailsCard user={owner} title="Owner" />}

      <LibraryNovelList library={library} />
    </Space>
  );
};
