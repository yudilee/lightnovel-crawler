import { UserAvatar } from '@/components/Tags/UserAvatar';
import { UserRoleTag } from '@/components/Tags/UserRoleTag';
import { UserStatusTag } from '@/components/Tags/UserStatusTag';
import { UserTierTag } from '@/components/Tags/UserTierTag';
import { type User } from '@/types';
import { formatDate } from '@/utils/time';
import { CalendarOutlined } from '@ant-design/icons';
import { Card, Col, Flex, Grid, Row, Space, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import md5 from 'spark-md5';
import { UserActionButtons } from './UserActionButtons';

const getGravatarProfile = async (email: string) => {
  const hash = md5.hash(email.trim().toLowerCase());
  const key = `__gravatar_${hash}`;
  const cache = localStorage.getItem(key);
  if (cache) {
    return JSON.parse(cache);
  }

  const resp = await fetch(`https://en.gravatar.com/${hash}.json`);
  const json = await resp.json();
  const data = json.entry;
  localStorage.setItem(key, JSON.stringify(data));
  return data;
};

export const UserListItemCard: React.FC<{
  user: User;
  hideActions?: boolean;
  onChange?: () => any;
  onClick?: React.MouseEventHandler<HTMLDivElement>;
}> = ({ user, hideActions, onChange, onClick }) => {
  const { lg } = Grid.useBreakpoint();

  const [displayName, setDisplayName] = useState<string>();

  useEffect(() => {
    if (!user.name?.trim()) {
      getGravatarProfile(user.email)
        .then((p) => setDisplayName(p.displayName))
        .catch(console.error);
    } else {
      setDisplayName(user.name.trim());
    }
  }, [user.name, user.email]);

  return (
    <Card
      onClick={onClick}
      hoverable={Boolean(onClick)}
      style={{ marginBottom: 5 }}
      styles={{
        body: { padding: lg ? undefined : 15 },
      }}
    >
      <Row align="middle" gutter={[25, 16]}>
        <Col flex="auto" style={{ width: '300px' }}>
          <Space size="middle" style={{ position: 'relative' }}>
            <UserAvatar size={48} user={user} />
            {displayName ? (
              <Flex vertical>
                <Typography.Text strong>
                  {hideActions ? (
                    displayName
                  ) : (
                    <Link to={`/admin/user/${user.id}`}>{displayName}</Link>
                  )}
                </Typography.Text>
                <Typography.Text
                  type={'secondary'}
                  style={{ whiteSpace: 'pre-wrap' }}
                >
                  {user.email}
                </Typography.Text>
              </Flex>
            ) : (
              <Flex vertical>
                <Typography.Text style={{ whiteSpace: 'pre-wrap' }}>
                  <Link to={`/admin/user/${user.id}`}>{user.email}</Link>
                </Typography.Text>
              </Flex>
            )}
          </Space>
        </Col>

        <Col flex="auto">
          <Flex wrap gap="10px" justify="space-between">
            <Flex wrap vertical gap="10px">
              <Flex gap="10px">
                <Typography.Text
                  strong
                  style={{ width: 70, textAlign: 'right' }}
                >
                  Role:
                </Typography.Text>
                <UserRoleTag value={user.role} />
              </Flex>
              <Flex gap="10px">
                <Typography.Text
                  strong
                  style={{ width: 70, textAlign: 'right' }}
                >
                  Status:
                </Typography.Text>
                <UserStatusTag value={user.is_active} />
              </Flex>
            </Flex>
            <Flex wrap vertical gap="10px">
              <Flex gap="10px">
                <Typography.Text
                  strong
                  style={{ width: 70, textAlign: 'right' }}
                >
                  Tier:
                </Typography.Text>
                <UserTierTag value={user.tier} />
              </Flex>
              <Flex gap="10px">
                <Typography.Text
                  strong
                  style={{ width: 70, textAlign: 'right' }}
                >
                  Joined:
                </Typography.Text>
                <Typography.Text>
                  <CalendarOutlined /> {formatDate(user.created_at)}
                </Typography.Text>
              </Flex>
            </Flex>
          </Flex>
        </Col>
        {!hideActions && (
          <Col
            flex="auto"
            style={{ width: '120px' }}
            onClick={(e) => e.preventDefault()}
          >
            <Flex
              wrap
              gap="10px"
              align="center"
              justify="end"
              style={{ minWidth: 100 }}
            >
              <UserActionButtons user={user} onChange={onChange} />
            </Flex>
          </Col>
        )}
      </Row>
    </Card>
  );
};
