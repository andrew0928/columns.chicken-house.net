using System;
using System.Data;
using System.Configuration;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.HtmlControls;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using BlogEngine.Core;
using System.IO;
using BlogEngine.Core.Web.Controls;
using System.Xml;
using System.Web.Caching;
using System.Collections;
using System.Collections.Generic;

/// <summary>
/// Summary description for Counter
/// </summary>
[Extension("PostViewCounter", "1.0", "<a href=\"http://columns.chicken-house.net\">chicken</a>")]
public class PostViewCounter
{
    private static ExtensionSettings _settings = null;

    public PostViewCounter()
	{
        Post.Serving += new EventHandler<ServingEventArgs>(OnPostServing);


        ExtensionSettings settings = new ExtensionSettings("PostViewCounter");

        settings.AddParameter(
            "MaxHitRecordCount", 
            "最多保留筆數:");
        settings.AddParameter(
            "HitRecordTTL", 
            "最長保留天數:");

        settings.AddValues(new string[] { "500", "90" });

        //settings.ShowAdd = false;
        //settings.ShowDelete = false;
        //settings.ShowEdit = true;
        settings.IsScalar = true;
        settings.Help = "設定 counter hit records 保留筆數及時間。只有在筆數限制內且沒有超過保留期限的記錄才會被留下來。";
        
        ExtensionManager.ImportSettings(settings);

        _settings = ExtensionManager.GetSettings("PostViewCounter");
    }

    public static int MaxHitRecordCount
    {
        get
        {
            return int.Parse(_settings.GetSingleValue("MaxHitRecordCount"));
        }
    }

    public static int HitRecordTTL
    {
        get
        {
            return int.Parse(_settings.GetSingleValue("HitRecordTTL"));
        }
    }



    private void OnPostServing(object sender, ServingEventArgs e)
    {
        IPublishable ipub = ((IPublishable)sender);
        string body = String.Empty;

        if (e.Location == ServingLocation.SinglePost && HttpContext.Current.Request.IsAuthenticated == false)
        {
            Counter.Hit(ipub.Id.ToString());
        }
    }









    public class Counter
    {
        private string _counterID = null;
        private string _dataFilePath = null;
        private string DataFilePath
        {
            get
            {
                return this._dataFilePath;
            }
        }

        public Counter(string counterID)
        {
            this._counterID = counterID;

            //
            //  build path
            //
            string dataFolder = Path.Combine(HttpContext.Current.Server.MapPath(BlogSettings.Instance.StorageLocation), "counter");
            if (Directory.Exists(DataFilePath) == false) Directory.CreateDirectory(dataFolder);
            this._dataFilePath = Path.Combine(dataFolder, this._counterID + ".xml");
        }

        public void Hit()
        {
            //
            //  add count and save to files. 要處理好 lock 的問題
            //
            FileStream fs = File.Open(
                this.DataFilePath,
                FileMode.OpenOrCreate,
                FileAccess.ReadWrite,
                FileShare.None);

            XmlDocument xmldoc = new XmlDocument();
            if (fs.Length == 0)
            {
                xmldoc.LoadXml("<?xml version=\"1.0\" encoding=\"utf-8\"?><counter />");
            }
            else
            {
                xmldoc.Load(fs);
                fs.Seek(0, SeekOrigin.Begin);
                fs.SetLength(0);

                this.Compact(xmldoc);
            }



            XmlElement hitelem = xmldoc.CreateElement("hit");
            xmldoc.DocumentElement.AppendChild(hitelem);

            hitelem.SetAttribute("time", DateTime.Now.ToString("s"));
            hitelem.SetAttribute("referer", HttpContext.Current.Request.ServerVariables["HTTP_REFERER"]);
            hitelem.SetAttribute("remote-host", HttpContext.Current.Request.ServerVariables["REMOTE_HOST"]);
            hitelem.SetAttribute("user-agent", HttpContext.Current.Request.ServerVariables["HTTP_USER_AGENT"]);

            xmldoc.Save(fs);
            fs.Close();
        }

        public void Compact()
        {
            if (File.Exists(this.DataFilePath) == false) return;

            FileStream fs = File.Open(
                this.DataFilePath,
                FileMode.Open,
                FileAccess.ReadWrite,
                FileShare.None);

            XmlDocument xmldoc = new XmlDocument();
            xmldoc.Load(fs);

            fs.Seek(0, SeekOrigin.Begin);
            fs.SetLength(0);

            this.Compact(xmldoc);

            xmldoc.Save(this.DataFilePath);
            fs.Close();
        }

        private void Compact(XmlDocument xmldoc)
        {
            //
            //  check compact settings
            //
            int padCount = 0;

            XmlNodeList hits = xmldoc.DocumentElement.SelectNodes("hit");
            foreach (XmlElement hit in hits)
            {
                if (DateTime.Parse(hit.GetAttribute("time")).AddDays(HitRecordTTL) > DateTime.Now && (hits.Count - padCount) < MaxHitRecordCount)
                {
                    break;
                }

                //
                //  timeout or exceed max count
                //
                hit.ParentNode.RemoveChild(hit);
                padCount++;
            }

            if (padCount > 0)
            {
                int baseCount = 0;
                if (xmldoc.DocumentElement.HasAttribute("base") == true)
                {
                    baseCount = int.Parse(xmldoc.DocumentElement.GetAttribute("base"));
                }
                xmldoc.DocumentElement.SetAttribute("base", (baseCount + padCount).ToString());
            }
        }

        public int GetTotalCount()
        {
            if (File.Exists(this.DataFilePath) == false)
            {
                return 0;
            }

            //
            //  從檔案載入總筆數。要透過 CACHE 輔助
            //
            string cacheKey = "counter-cache-" + this._counterID;
            int? value = HttpRuntime.Cache[cacheKey] as int?;
            if (value == null)
            {
                XmlDocument xmldoc = new XmlDocument();
                xmldoc.Load(this.DataFilePath);

                int baseCount = (xmldoc.DocumentElement.HasAttribute("base")) ? (int.Parse(xmldoc.DocumentElement.GetAttribute("base"))) : (0);
                int hitCount = xmldoc.DocumentElement.SelectNodes("hit").Count;

                value = baseCount + hitCount;
                HttpRuntime.Cache.Insert(
                    cacheKey,
                    value,
                    new CacheDependency(this.DataFilePath));
            }
            return value.Value;
        }

        public static int GetTotalCount(string counterID)
        {
            return (new Counter(counterID)).GetTotalCount();
        }

        public static void Hit(string counterID)
        {
            (new Counter(counterID)).Hit();
        }

        public static void Compact(string counterID)
        {
            (new Counter(counterID)).Compact();
        }

        public static int TotalPostsCount()
        {
            int total = 0;

            foreach (Post post in Post.Posts)
            {
                total += GetTotalCount(post.Id.ToString());
            }

            return total;
        }
    }
}
