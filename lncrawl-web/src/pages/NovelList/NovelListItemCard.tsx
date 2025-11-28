import FallbackImage from '@/assets/no-image.svg';
import { Favicon } from '@/components/Favicon';
import { API_BASE_URL } from '@/config';
import { Auth } from '@/store/_auth';
import type { Novel } from '@/types';
import { Card, Flex, Image, Tooltip, Typography } from 'antd';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

export const NovelListItemCard: React.FC<{ novel: Novel }> = ({ novel }) => {
  const navigate = useNavigate();
  const token = useSelector(Auth.select.authToken);

  return (
    <Tooltip
      title={
        <Flex wrap gap="5px">
          <Typography.Text strong>{novel.title}</Typography.Text>
          <Typography.Text type="secondary">({novel.domain})</Typography.Text>
        </Flex>
      }
    >
      <Card
        hoverable
        style={{
          height: '100%',
          overflow: 'clip',
          position: 'relative',
          userSelect: 'none',
          background: '#dee2e6',
        }}
        onClick={() => navigate(`/novel/${novel.id}`)}
        styles={{
          body: {
            padding: 0,
            aspectRatio: 0.7,
          },
        }}
      >
        <Image
          alt="cover"
          preview={false}
          src={`${API_BASE_URL}/static/${novel.cover_file}?token=${token}`}
          fallback={FallbackImage}
          loading="lazy"
          fetchPriority="low"
          style={{
            objectFit: 'cover',
            aspectRatio: 3 / 4,
            minHeight: '100%',
            maxHeight: '50vh',
          }}
        />
        <Favicon
          size="small"
          url={novel.url}
          style={{
            position: 'absolute',
            top: 3,
            left: 5,
            backdropFilter: 'blur(10px)',
          }}
        />
        {novel.title && novel.title !== '...' && (
          <Typography.Paragraph
            strong
            ellipsis={{ rows: 2 }}
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              margin: 0,
              padding: '3px 5px',
              textAlign: 'center',
              fontSize: '12px',
              backdropFilter: 'blur(5px)',
              background: 'rgba(0, 0, 0, 0.5)',
            }}
          >
            {novel.title}
          </Typography.Paragraph>
        )}
      </Card>
    </Tooltip>
  );
};
