import FallbackImage from '@/assets/no-image.svg';
import { API_BASE_URL } from '@/config';
import { Auth } from '@/store/_auth';
import type { Novel } from '@/types';
import { getGradientForId } from '@/utils/gradients';
import { formatDate } from '@/utils/time';
import { ExportOutlined } from '@ant-design/icons';
import {
  Card,
  Descriptions,
  Divider,
  Flex,
  Grid,
  Image,
  Space,
  Tag,
  Tooltip,
  Typography,
} from 'antd';
import { useState } from 'react';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { Favicon } from '../../components/Favicon';
import { NovelActionButtons } from './NovelActionButtons';

export const NovelDetailsCard: React.FC<{
  novel: Novel;
  showActions?: boolean;
  withPageLink?: boolean;
}> = ({ novel, showActions, withPageLink }) => {
  const { lg } = Grid.useBreakpoint();

  const token = useSelector(Auth.select.authToken);
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [showMore, setShowMore] = useState<boolean>(false);

  return (
    <Card
      variant="outlined"
      styles={{
        title: {
          padding: '8px 0',
          marginRight: 10,
        },
      }}
      title={
        <Flex vertical>
          <Space size="small">
            <Favicon url={novel.url} />
            <Typography.Text type="secondary" style={{ fontSize: '18px' }}>
              {novel.domain}
            </Typography.Text>
          </Space>
          <Typography.Text style={{ fontSize: '24px', whiteSpace: 'wrap' }}>
            {withPageLink ? (
              <Link to={`/novel/${novel.id}`}>{novel.title}</Link>
            ) : (
              novel.title
            )}
          </Typography.Text>
        </Flex>
      }
      extra={[
        <Tooltip title={'Original source'}>
          <Typography.Link
            href={novel.url}
            target="_blank"
            rel="noreferrer noopener"
            style={{ fontSize: '24px' }}
          >
            <ExportOutlined />
          </Typography.Link>
        </Tooltip>,
      ]}
    >
      <Flex gap="20px" vertical={!lg}>
        <Flex vertical align="center" justify="flex-start" gap="5px">
          <Image
            alt="Novel Cover"
            src={`${API_BASE_URL}/static/${novel.cover_file}?token=${token}`}
            fallback={FallbackImage}
            style={{
              display: 'block',
              objectFit: 'cover',
              borderRadius: 8,
              width: 'auto',
              maxWidth: '225px',
              height: '300px',
              background: getGradientForId(novel.id),
            }}
          />
        </Flex>
        <Flex vertical flex="auto" gap="5px">
          <Descriptions
            size="small"
            layout="horizontal"
            column={lg ? 2 : 1}
            bordered
            items={[
              {
                label: 'Authors',
                span: 2,
                children: novel.authors,
              },
              {
                label: 'Volumes',
                children: novel.volume_count,
              },
              {
                label: 'Chapters',
                children: novel.chapter_count,
              },
              {
                label: 'Created',
                children: formatDate(novel.created_at),
              },
              {
                label: 'Last Update',
                children: formatDate(novel.updated_at),
              },
            ]}
          />

          <Typography.Paragraph
            ellipsis={{ rows: showMore ? undefined : 5 }}
            style={{
              overflow: 'hidden',
              textAlign: 'justify',
              whiteSpace: 'wrap',
            }}
            ref={(el) => {
              if (!el) return;
              setHasMore(Math.abs(el.scrollHeight - el.clientHeight) > 10);
            }}
          >
            <div
              dangerouslySetInnerHTML={{
                __html: novel.synopsis || '<p>No synopsis available</p>',
              }}
            />
          </Typography.Paragraph>

          {(hasMore || showMore) && (
            <Typography.Link
              italic
              onClick={() => setShowMore((v) => !v)}
              style={{ textAlign: showMore ? 'left' : 'right' }}
            >
              {showMore ? '< See less' : 'See more >'}
            </Typography.Link>
          )}
        </Flex>
      </Flex>

      {novel.tags && Array.isArray(novel.tags) && novel.tags.length > 0 && (
        <Flex wrap gap={5} justify="center" style={{ width: '100%' }}>
          <Divider size="small" />
          {novel.tags.map((tag) => (
            <Tag key={tag} style={{ textTransform: 'capitalize' }}>
              {tag.toLowerCase()}
            </Tag>
          ))}
        </Flex>
      )}

      {showActions && (
        <>
          <Divider size="small" />
          <NovelActionButtons novel={novel} />
        </>
      )}
    </Card>
  );
};
