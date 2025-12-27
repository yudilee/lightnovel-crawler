import FallbackImage from '@/assets/no-image.svg';
import { Favicon } from '@/components/Favicon';
import { API_BASE_URL } from '@/config';
import { Auth } from '@/store/_auth';
import type { Novel } from '@/types';
import { getGradientForId } from '@/utils/gradients';
import { Card, Image, Typography } from 'antd';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

export const NovelListItemCard: React.FC<{ novel: Novel }> = ({ novel }) => {
  const navigate = useNavigate();
  const token = useSelector(Auth.select.authToken);

  return (
    <Card
      hoverable
      style={{
        height: '100%',
        overflow: 'clip',
        position: 'relative',
        userSelect: 'none',
        background: getGradientForId(novel.id),
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      }}
      onClick={() => navigate(`/novel/${novel.id}`)}
      styles={{
        body: {
          padding: 0,
          aspectRatio: 0.7,
        },
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.15)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
      }}
    >
      <Image
        alt="cover"
        preview={false}
        src={`${API_BASE_URL}/static/${novel.cover_file}?token=${token}`}
        fallback={FallbackImage}
        fetchPriority="low"
        style={{
          objectFit: 'cover',
          height: '100%',
          width: '100%',
        }}
        styles={{
          root: {
            aspectRatio: 3 / 4,
            minHeight: '100%',
            maxHeight: '50vh',
          },
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
  );
};
