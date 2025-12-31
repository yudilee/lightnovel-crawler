import { Button, Modal, Typography } from 'antd';
import type { LinkProps } from 'antd/es/typography/Link';
import { useState } from 'react';

export const PrivacyPolicy: React.FC<LinkProps> = (props) => {
  const [error, setError] = useState<string>();
  const [privacyModalOpen, setPrivacyModalOpen] = useState<boolean>(false);
  const [privacyContent, setPrivacyContent] = useState<string>('');
  const [loadingPrivacy, setLoadingPrivacy] = useState<boolean>(false);

  const loadPrivacyPolicy = async () => {
    if (privacyContent) {
      setPrivacyModalOpen(true);
      return;
    }
    setLoadingPrivacy(true);
    try {
      const response = await fetch('/PRIVACY_POLICY.html');
      if (!response.ok) {
        throw new Error(`Failed to load: ${response.statusText}`);
      }
      const html = await response.text();
      setPrivacyContent(html);
      setPrivacyModalOpen(true);
    } catch (err) {
      setError('Failed to load privacy policy. Please try again later.');
      console.error('Error loading privacy policy:', err);
    } finally {
      setLoadingPrivacy(false);
    }
  };

  return (
    <>
      <Typography.Link
        {...props}
        onClick={(e) => {
          e.preventDefault();
          loadPrivacyPolicy();
        }}
        style={{
          padding: 0,
          fontSize: 'inherit',
          fontFamily: 'inherit',
          fontWeight: 'inherit',
          ...props.style,
        }}
      >
        Privacy Policy
      </Typography.Link>

      <Modal
        title="Privacy Policy"
        open={privacyModalOpen}
        onCancel={() => setPrivacyModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setPrivacyModalOpen(false)}>
            Close
          </Button>,
        ]}
        width={800}
        style={{ top: 20 }}
      >
        <div
          style={{
            maxHeight: '70vh',
            overflowY: 'auto',
            padding: '16px 0',
          }}
        >
          {loadingPrivacy ? (
            <Typography.Text>Loading...</Typography.Text>
          ) : error ? (
            <Typography.Text type="danger">{error}</Typography.Text>
          ) : (
            <div
              className="policy-content"
              dangerouslySetInnerHTML={{ __html: privacyContent }}
              style={{
                lineHeight: '1.6',
              }}
            />
          )}
        </div>
      </Modal>
    </>
  );
};
